#encoding=utf8
from db import Database
import os,os.path
from config import ignore_file,ignore_dir,file_ex2type

import zipfile
import rarfile
import chardet
class Library:
    '''
    Library 作为媒体库,其主要包括虚拟的"库"概念与实体目录之间的映射

    create table library
    (
        id serial primary key,
        name varchar(128) not null,
        dir varchar(1024),
        status varchar(16) check( status in ('syncing','synced','unsync')),
        version int,
        lib_type varchar(1024) not null default 'photo',
        skip_dir varchar(1024) not null default '',
        skip_file varchar(1024) not null default '',
        support_file varchar(1024) not null default ''
    );
    create unique index unq_library_name on library(name);
    
    create table item(
        id serial primary key,
        name text,
        cover int,
        path text,
        parent int,
        library_id int,
        version int,
        order_id int not null default -1,
        item_type varchar(128) not null default 'file'
    )
    create unique index unq_item_path on item(library_id,path);
    create index idx_libid_item_id on item(library_id,id);
    
    create table lib_user(
        username varchar(128),
        passwd varchar(128)
    )
    create unique index  unq_user on lib_user(username);
    '''

    def __init__(self, library_id,name,dir,status,version):
        self.id=library_id
        self.name=name
        self.dir=dir
        self.status=status
        self.version=version
        self.new_version=3

    def sync(self):
        '''
        同步媒体库
        三步走:
        1 扫描目录树
        采用python的walk方法
        2 入文件库与目录库
        执行入库,如果文件已经存在(绝对路径重复),则更新其版本号,否则插入数据
        3 生成目录库封面
        首先从file库生成最基础的目录库封面,然后处理没有封面的目录(多见于父目录)
        除了首次同步外,无封面目录应该是少数
        无封面目录处理流程:
            查询所有无封面目录,逐个处理: 寻找其子目录封面,如果子目录不存在封面,则继续向下查询,直到找到封面后逐个更新
        4 更新library版本号,删除旧版本数据
        '''
        self.walk()
        self.gen_cover()
        self.sync_end()

    def sync_end(self):
        with Database() as db:
            self.analysis()
            db.execute("update library set version=%s,status='synced' where id=%s",(self.new_version,self.id))
            self.version=self.new_version

    def gen_cover(self):
        with Database() as db:
            db.execute("update item set cover=cover_map.cover_id from (select min(id) cover_id,parent from item where item_type='file' and  library_id=%s group by parent) cover_map where item.id=cover_map.parent ",(self.id,))
            db.execute("commit")
            '''
            这里可能会有永远没有封面的目录 
            如果前一次跑后，无封面目录数量没有变化，认为已经完成，中断执行
            另外，为了避免while无限循环，这里for 100
            '''
            last_count=0
            for i in range(100):
                db.execute("update item set cover=cover_map.cover_id from (select min(cover) cover_id,parent from item where item_type='dir' and cover !=0 and  library_id=%s group by parent) cover_map where item.id=cover_map.parent and item.cover=0",(self.id,))
                db.execute("commit")
                rows=db.select("select * from item where parent in (select id from item where library_id=%s and cover =0 and item_type='dir')",(self.id,))

                if len(rows)==last_count:
                    break
                else:
                    last_count=len(rows)

            db.execute("delete from item where cover<1 and item_type='dir' and library_id=%s",(self.id,))
    def walk(self):
        with Database() as db:
            self.new_version=self.version+1
            version=self.new_version
            def insert_directory(parentname,dirs):
                '''
                首先查询父目录id,如果未命中,则报错
                然后根据父目录id入库
                如果发现已经存在,则升级其版本id
                注:当前仅考虑逐个insert,后续如果发现性能问题,另外考虑批量手段
                '''
                rows=db.select("select id from item where library_id=%s and path=%s",(self.id,parentname))
                if not rows:
                    parent=0
                else:
                    parent=rows[0]['id']

                for name in dirs:
                    if name in ignore_dir:
                        continue
                    db.execute(f'''insert into item(name,cover,path,library_id,parent,version,item_type) values(%s,0,%s,{self.id},{parent},{version},'dir') ON CONFLICT (library_id,path) do update set version={version} ''',(name,parentname+os.path.sep+name))

            def insert_files(parentname,files):
                '''
                首先查询父目录id,如果未命中,则报错
                然后根据父目录id入库
                如果发现已经存在,则升级其版本id
                注:当前仅考虑逐个insert,后续如果发现性能问题,另外考虑批量手段
                '''
                rows=db.select("select id from item where library_id=%s and path=%s",(self.id,parentname))
                if not rows:
                    parent=0                    
                    if parentname!=self.dir:
                        # 只有已经跳过的文件夹才会有不存在库中的问题
                        return 
                else:
                    parent=rows[0]['id']
                for name in files:
                    if name in ignore_file:
                        continue
                    if name.startswith('.'):
                        continue
                    if name.split('.')[-1].lower() in ("jpg",'png','bmp','jpeg','gif','mp4','avi','mkv','webm','flv','mov','mp3','wav','flac'):
                        db.execute('''insert into item(name,path,parent,library_id,version,item_type) values(%s,%s,%s,%s,%s,'file')
                        ON CONFLICT (library_id,path) do update set version=%s ''',(name,parentname+os.path.sep+name,parent,self.id,version,version))
                    if name.split('.')[-1].lower() in ("cbz",'cbr','zip','rar'):
                        file_ex=name.split(".")[-1].lower()
                        full_path=parentname+os.path.sep+name
                        rows=db.select(f'''insert into item(name,cover,path,library_id,parent,version,item_type,file_type) values(%s,0,%s,{self.id},{parent},{version},'dir','compress') ON CONFLICT (library_id,path) do update set version={version}  returning id ''',(name,full_path))
                        c_id=rows[0]['id']
                        if file_ex in ("zip",'cbz'):
                            C_cls=zipfile.ZipFile
                        elif file_ex in ("rar",'cbr'):
                            C_cls=rarfile.RarFile
                        else:
                            # 对于后缀名不是指定的，不做处理
                            return None
                        try:
                            with C_cls(full_path) as zf:
                                for fname in zf.namelist():
                                    # 处理压缩文件内部的路径问题
                                    real_name=fname.split("/")[-1]
                                    if fname in ignore_file or real_name in ignore_file:
                                        continue
                                    if fname.startswith('.') or real_name.startswith('.'):
                                        continue
                                    if fname.startswith('_') or real_name.startswith('.'):
                                        continue
                                    if fname.split('.')[-1].lower() not in ("jpg",'png','bmp','jpeg','gif'):# 目前压缩文件内仅考虑图片
                                        continue
                                    db.execute(f'''insert into item(name,cover,path,library_id,parent,version,item_type) values(%s,0,%s,{self.id},{c_id},{version},'file') ON CONFLICT (library_id,path) do update set version={version} ''',(fname,full_path+os.path.sep+fname))
                                db.execute("commit")
                        except:
                            print("错误的压缩文件：",full_path)


                    
                    

            for root, dirs, files  in os.walk(self.dir):
                import time
                if root.split(os.path.sep)[-1] in ignore_dir:
                    continue
                insert_directory(root,dirs)
                insert_files(root,files)
                db.execute("commit")
            db.execute("delete from item where library_id=%s and version=%s",(self.id,self.version))
            db.execute("commit")


    def __str__(self):
        return f"LIBRARY ID:{self.id} NAME:{self.name} DIR: {self.dir} STATUS:{self.status} VERSION:{self.version}"

    def __repr__(self):
        return self.__str__()

    def analysis(self):
        '''
        这里对具体文件信息进行分析，处理到对应的电影，图片，音乐表,这个表主键认为与item主键关联
        目前仅处理文件类型，创建时间，修改时间三个字段，其他后续更新处理
        '''
        with Database() as db:
            before=0
            while True:
                files= db.select("select id,name,path,parent,(select p.file_type from item p where p.id=item.parent) as parent_file_type from item where file_type='file' and  library_id=%s",(self.id,) )
                if len(files)==before:
                    break
                before=len(files)
                '''
                逐个文件采用stat调用，判断stat以及文件类型
                '''
                for item in files:
                    if '.' in item['name']:
                        ptype = item['name'].split('.')[-1]
                        # 对于压缩文件中的文件，cutime不做处理，仅处理file_type
                        if item['parent_file_type']=='compress':
                            db.execute("update item set file_type=%s where id=%s",(file_ex2type(item['name']),item['id']))
                        else:
                            stat=os.stat(item['path'])
                            db.execute("update item set ctime=to_timestamp(%s),utime=to_timestamp(%s),file_type=%s where id=%s",(stat.st_ctime,stat.st_mtime,file_ex2type(item['name']),item['id']))


    @staticmethod
    def get(library_id):
        with Database() as db:
            rows=db.select("select id,name,dir,status,version from library where id=%s",(library_id,))
            if not rows:
                return None
            else:
                row=rows[0]
                return Library(row['id'],row['name'],row['dir'],row['status'],row['version'])

    @staticmethod
    def librarys(name=None):
        rList=[]
        with Database() as db:
            if name:
                rows=db.select("select id,name,dir,status,version,library_type from library where name like %s order by id",(name,))
            else:
                rows=db.select("select id,name,dir,status,version,library_type from library order by id")
            for row in rows:
                rList.append(Library(row['id'],row['name'],row['dir'],row['status'],row['version']))
        return rList
    @staticmethod
    def add(name,dir,lib_type,skip_dir,skip_file,support_file):
        with Database() as db:
            return db.execute("insert into library(name,dir,status,version,lib_type,skip_dir,skip_file,support_file) values(%s,%s,%s,%s,%s,%s,%s,%s)",(name,dir,'unsync',0,lib_type,skip_dir,skip_file,support_file))
    @staticmethod
    def changeName(library_id,name):
        with Database() as db:
            db.execute("update library set name=%s where id=%s",(name,library_id))

    @staticmethod
    def drop(library_id):
        with Database() as db:
            db.execute("delete from item where library_id=%s",(library_id,))
            db.execute("delete from library where id=%s",(library_id,))

    
if __name__ == "__main__":
    # Library.add("photos",'/Users/liuwei/comic/[G-Power! (SASAYUKi)]','photo','','','jpg,gif')
    lib=Library.get(8)
    # lib.id=100
    lib.sync()
    #with zipfile.ZipFile("/data1/data/psiupuxa.zip") as zf:
    #    for name in zf.namelist():
    #        byte=bytes(name,'utf8')
    #        print(name,byte,chardet.detect(byte))
    #        f=zf.open(name)
    #        b=f.read()
    #        if name.startswith('__'):
    #            continue
    #        f=open('/data1/data/zf.jpg','wb+')
    #        f.write(b)
    #        f.close()
