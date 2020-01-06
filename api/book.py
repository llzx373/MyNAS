#encoding=utf8
from db import Database
'''
这部分主要实现写作部分的功能

后端接口提供

层级：
    库 注：设置目录为备份目标目录
        章节
            封面
            简介
            笔记
    tag
        
create table chapter
(
    id serial primary key,
    title varchar(128) not null,
    summary varchar(1024)not null default '',
    note text,
    cover bytea,
    status varchar(128) not null default '写作中',
    word_count int, #这个字段主要用于看主视角的时候，避免遍历
    dest_word_count int not null default -1, #设置目标字数 主要用于查看进度
    ctime timestamp,
    utime timestamp,
    parent int,
    order_id int,
    library_id int,
    context text,
    chapter_type varchar(128) not null default 'chapter' # 这里可能的值为chapter（章节）Part（卷）Book（书） 仅关联到展示图标，无关其他
)
create index idx_chapter on chapter(library_id,id);

'''

class Chapter(object):

    def __init__(self,chapter_id,title,summary,note,cover,status,word_count,dest_word_count,ctime,utime,parent,order_id,library_id,chapter_type,context,update_id,chapter_word_count):
        self.chapter_id=chapter_id
        self.id=chapter_id
        self.title=title
        self.summary=summary
        self.note=note
        self.cover=cover
        self.status=status
        self.word_count=word_count
        self.dest_word_count=dest_word_count
        self.ctime=ctime
        self.utime=utime
        self.parent=parent
        self.order_id=order_id
        self.library_id=library_id
        self.chapter_type=chapter_type
        if context is None:
            context=''
        self.context=context
        self.item_type='chapter'
        self.update_id=update_id
        self.chapter_word_count=chapter_word_count
    

    def update(self):
        '''
        
        字数部分单独处理
        '''
        with Database() as db:
            db.execute("update chapter set title=%s ,summary=%s,note=%s,status=%s,utime=now(),chapter_type=%s,context=%s,update_id=%s where id=%s",(self.title ,self.summary,self.note,self.status,self.chapter_type,self.context,self.update_id,self.chapter_id))
            # newwordcount=len(self.context)-self.word_count
            # db.execute("update chapter set word_count=0 where id=%s",(self.context,))
            # 这里原本打算直接更新父亲级别，但实际上来看，维护过于复杂，章节字数维护让 chapter count处理
            # for parent in self.getParents():
                # db.execute("update chapter set word_count=%s where id=%s",(newwordcount+parent['word_count'],parent['id']))
            self.utime=db.select("select utime from chapter where id=%s",(self.chapter_id,))[0]['utime']
        Chapter.syncWordCount(self.library_id)

    def newChapter(self,title,summary):
        new_chapter_id=Chapter.innerNewChapter(self.library_id,title,summary,None,self.chapter_id)
        '''
        处理order_id
        新章节默认在最后一个位置
        '''
        order_id=-1
        with Database() as db:
            rows=db.select("select max(order_id) max_id from chapter where parent=%s",(self.chapter_id,),dict_result=True)
            if rows:
                order_id=rows[0]['max_id']+1
            else:
                order_id=1
            db.execute("update chapter set order_id=%s where id=%s",(order_id,new_chapter_id))
        return Chapter.getChapter(new_chapter_id)


    def getParents(self):
        with Database() as db:
            '''
            获取父级别
            '''
            parents=[]
            current_chapter=self.chapter_id
            while True:
                rows=db.select("select id,title,summary,parent,word_count from chapter where id=%s",(current_chapter,),dict_result=True)
                if rows:
                    chapter=rows[0]
                    if chapter['parent']==0:
                        parents.append(chapter)
                        break
                    else:
                        parents.append(chapter)
                        current_chapter=chapter['parent']
                else:
                    break
            self.parents=parents
        return self.parents

    def preview(self):
        '''
        根据设置的参数，拼接markdown
        规则如下： 
            标题名称为 #*level 全级别 order id title
            空一行
            正文 // 这里不再处理正文的标题标记，认为为编辑者自己控制
        '''
        tree=self.getChildren(True,False)
        stasks=[[0,"",tree],]
        context=''
        '''
        树遍历办法：
            深度优先
            栈中取出当前节点（栈顶为当前chapter）-> 如果没有子节点，生成正文后，继续下一个栈
                                            -> 如果有子节点，逆序入栈，生成正文后，继续下一个栈
        '''
        with Database() as db:
            while True:
                if len(stasks)==0:
                    break
                level,order_id_prefix,chapter=stasks.pop()
                if level>0:
                    title_level='#'*level
                    context=context+f"\n{title_level} {order_id_prefix}{chapter['order_id']} {chapter['title']}\n\n"
                rows=db.select("select context from chapter where id=%s",(chapter['id'],))
                if rows:
                    if rows[0]['context'] is not None:
                        context=context+"\n"+rows[0]['context']+'\n'
                chapter['children'].reverse()
                for child in chapter['children']:
                    if level==0:
                        stasks.append([level+1,"",child])
                    else:
                        stasks.append([level+1,order_id_prefix+f"{chapter['order_id']}.",child])
        return context

    def getChildren(self,all=False,asList=True):
        with Database() as db:
            '''
            获取子级别
            all 获取所有子chapter
            '''
            
            self.children=db.select("select id,title,summary,parent,order_id,word_count,dest_word_count,ctime,utime,status,char_length(context) chapter_word_count from chapter where parent=%s",(self.chapter_id,),dict_result=True)
            if not all: 
                return self.children
        
            list_result=[]
            current_chapter=self.chapter_id
            current_children=[self.chapter_id,]
            '''
            这里并没有采用遍历树而是采用了逐步深度查找，数据库中每个层级最多仅查询一次,目前仅考虑获取全部chapter，不考虑层级问题
            '''
            while True:
                children=db.select("select id,title,summary,parent,order_id,chapter_type,word_count,dest_word_count,ctime,utime,status,char_length(context) chapter_word_count from chapter where parent in ("+ ','.join([str(i) for i in current_children]) +")",dict_result=True)
                if not children:
                    break
                current_children=[]
                for child in children:
                    list_result.append(child)
                    current_children.append(child['id'])
            if asList:
                return list_result
            '''
            对于需要父子结果的情况来说，另外处理
            1 处理为字典
            '''
            class TreeNode:
                def __init__(self,id,title,summary,parent,chapter_type,order_id,word_count,dest_word_count,ctime,utime,status,chapter_word_count):
                    self.id=id
                    self.title=title
                    self.summary=summary
                    self.parent=parent
                    self.order_id=order_id
                    self.chapter_type=chapter_type
                    self.children=[]
                    self.word_count=word_count
                    self.dest_word_count=dest_word_count
                    self.ctime=ctime
                    self.utime=utime
                    self.status=status
                    self.chapter_word_count=chapter_word_count
                
                def getTree(self):
                    self.children.sort(key=lambda k: k.order_id)
                    return {
                        'id':self.id,
                        'title':self.title,
                        'summary':self.summary,
                        'parent':self.parent,
                        'order_id':self.order_id+1,
                        'chapter_type':self.chapter_type,
                        'children':[child.getTree() for child in self.children],
                        'word_count':self.word_count,
                        'dest_word_count':self.dest_word_count,
                        'ctime':self.ctime,
                        'utime':self.utime,
                        'status':self.status,
                        'chapter_word_count':self.chapter_word_count
                    }

            nodes={item['id']:TreeNode(**item)  for item in list_result}
            nodes[self.chapter_id]=TreeNode(self.chapter_id,self.title,self.summary,self.parent,self.chapter_type,self.order_id,self.word_count,self.dest_word_count,self.ctime,self.utime,self.status,self.chapter_word_count)
            
            '''
            返回父子结构
            '''
            for node in nodes.values():
                if node.parent in nodes:
                    nodes[node.parent].children.append(node)
            return nodes[self.chapter_id].getTree()

    def drop(self):
        children=self.getChildren(all=True)
        with Database() as db:
            if children:
                db.execute("delete from chapter where id in ("+','.join([str(child['id']) for child in children])+")")
            db.execute("delete from chapter where id=%s",(self.chapter_id,))
            '''
            更新order id 为了顺带修复order缺号问题，这里直接重排order id
            '''
            rows=db.select("select id,order_id from chapter where parent=%s",(self.parent,))
            cps=[]
            for row in rows:
                cps.append(
                    {
                        'id':row['id'],
                        'order_id':row['order_id']
                    }
                )
            cps.sort(key=lambda k: k['order_id'])
            for index,cp in enumerate(cps):
                db.execute("update chapter set order_id=%s where id=%s",(index,cp['id']))


    def changePositon(self,dest_chapter_id,dest_position):
        '''
        所有操作均在一个事务，保证一致性
        这里有三个可能的dest_position
        首先抽离出当前chapter，所有chapter>order id的-1 （设置chapter的父节点为-1（对其他节点不可见））

        before：设置order id为目标的order id 确定到目标节点的order id，原先父节点下所有order id>=(包括新目标节点)的，全部+1 设置当前chapter的父节点为新节点父节点，
        after：设置order id为目标的order id+1 确定到目标节点的order id，原先父节点下所有order id>(不包括新目标节点)的，全部+1 设置当前chapter的父节点为新节点父节点，
        inner：设置当前chapter父节点为目标节点，设置order id为目标节点下子节点最高的一个（如果没有则为1）

        
        '''
        with Database() as db:
            db.execute("update chapter set parent=-1 where id=%s",(self.chapter_id,))
            db.execute("update chapter set order_id=order_id-1 where parent=%s and order_id>%s ",(self.parent,self.order_id))
            '''
            考虑到树结构的复杂性，应该是全局锁来保证避免并发更新
            '''
            dest_chapter=Chapter.getChapter(dest_chapter_id)
            if dest_position=='before':
                db.execute("update chapter set order_id=%s where id=%s",(dest_chapter.order_id,self.chapter_id))
                db.execute("update chapter set order_id=order_id+1 where parent=%s and order_id>=%s ",(dest_chapter.parent,dest_chapter.order_id))
                db.execute("update chapter set parent=%s where id=%s",(dest_chapter.parent,self.chapter_id))
            if dest_position=='after':
                db.execute("update chapter set order_id=%s where id=%s",(dest_chapter.order_id+1,self.chapter_id))
                db.execute("update chapter set order_id=order_id+1 where parent=%s and order_id>%s ",(dest_chapter.parent,dest_chapter.order_id))
                db.execute("update chapter set parent=%s where id=%s",(dest_chapter.parent,self.chapter_id))
            if dest_position=='inner':
                rows=db.select("select max(order_id) order_id from chapter where parent=%s",(dest_chapter_id,))
                if rows:
                    if rows[0]['order_id'] is None:
                        new_order=0
                    else:
                        new_order=rows[0]['order_id']+1
                    db.execute("update chapter set parent=%s,order_id=%s where id=%s",(dest_chapter_id,new_order,self.chapter_id))
                else:
                    db.execute("update chapter set parent=%s,order_id=%s where id=%s",(dest_chapter_id,1,self.chapter_id))
        '''
        新事务重新获取parent，sort id
        '''
        chapter=Chapter.getChapter(self.chapter_id)
        self.parent=chapter.parent
        self.order_id=chapter.order_id
    
    @staticmethod
    def syncWordCount(library_id):
        '''
        重新同步字数统计
        '''
        with Database() as db:
            '''
            从最后一级逐个级别向上汇总

            首先从顶级 逐个级别汇总当前级别chapter到chapters
            然后从最末尾节点开始统计处理
            每个节点字数都是 下级字数+本章节正文字数
            '''
            chapters_list=[]
            chapters={}
            children=[0,]
            while True:
                rows=db.select("select id,parent,char_length(context) chapter_word_count from chapter where library_id="+str(library_id)+" and parent in ("+ ','.join([str(i) for i in children]) +")")
                children=[]
                if not rows:
                    break
                for row in rows:
                    if not row['chapter_word_count']:
                        chapter_word_count=0
                    else:
                        chapter_word_count=row['chapter_word_count']
                    chapters[row['id']]={
                        'id':row['id'],
                        'parent':row['parent'],
                        'chapter_word_count':chapter_word_count,
                        'word_count':0
                    }
                    children.append(row['id'])
                chapters_list.append(children)
            while True:
                if len(chapters_list)==0:
                    break
                inner_chapters=chapters_list.pop()
                for chapter in inner_chapters:
                    chapters[chapter]['word_count']+=chapters[chapter]['chapter_word_count']
                    if chapters[chapter]['parent']==0:
                        continue
                    chapters[chapters[chapter]['parent']]['word_count'] +=chapters[chapter]['word_count']
            for k,v in chapters.items():
                db.execute("update chapter set word_count=%s where id=%s",(v['word_count'],k))

            
            


    @staticmethod
    def newBook(library_id,title,summary,cover):
        # 新书单独处理为parent=0 的chapter
        return Chapter.innerNewChapter(library_id,title,summary,cover,0)

    @staticmethod
    def innerNewChapter(library_id,title,summary,cover,parent):
        # 新章节需要处理parent
        with Database() as db:
            db.execute("insert into chapter (title,summary,cover,ctime,utime,parent,order_id,library_id) values(%s,%s,%s,now(),now(),%s,-1,%s)",(title,summary,cover,parent,library_id))
            return db.select("select currval('chapter_id_seq') insert_id",dict_result=True)[0]['insert_id']

    @staticmethod
    def getChapter(chapter_id):
        with Database() as db:
            rows=db.select("select id chapter_id,title,summary,note,cover,status,word_count,dest_word_count,ctime,utime,parent,order_id,library_id,chapter_type,context,update_id,char_length(context) chapter_word_count from chapter where id=%s",(chapter_id,),dict_result=True)
            if rows:
                return Chapter(**rows[0])
            else:
                return None



if __name__ == "__main__":
    # cid=Chapter.newBook(3,'新小说','简介',None)
    chapter=Chapter.getChapter(71)
    print(chapter.preview())
    # Chapter.syncWordCount(3)
    # chapter.drop()
    # chapter.update()
    # newchapter=chapter.newChapter("新章节",'')
    # newchapter2=newchapter.newChapter("🎧新章节",'')
    # newchapter2.context="newchapter2"
    # newchapter2.update()
    # print(newchapter2.getParents())
    # print(chapter.getChildren())
    # print(chapter.getChildren(all=True,asList=False))
