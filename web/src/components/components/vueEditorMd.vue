<template>
    <div id="editor-md" class="main-editor">
        <link rel="stylesheet" href="/static/plug/editor.md/css/editormd.min.css">
        <div id="editor">
            <textarea class="editormd-textarea" v-text="value"></textarea>
        </div>
    </div>
</template>
<script>
    import $script from 'scriptjs';
    import $ from "jquery";
    export default {
        name:"vueEditorMd",
        props:{
            value:{
                type:String,
                default:""
            },
            placeholder:{
                type:String,
                default:"欢迎使用vue-editor-md"
            },
            tooBars:{
                type:Array,
                default(){
                    return [
                        "undo","redo",
                        "|",
                        "bold","del","italic","quote",
                        "|",
                        "list-ul","list-ol","hr",
                        "|",
                        "link","reference-link","code","code-block","datetime",
                        "|",
                        "file",
                        "||",
                        "watch","preview","fullscreen",
                        "|",
                        "help"
                    ]
                }
            },
            theme:{
                type:Object,
                default(){
                    return {
                        editor:"default",//dark default
                        previewTheme:"default",//dark default
                        editorTheme:"default"
                    }
                }
            },
            size:{
                type:Object,
                default(){
                    return {
                        width:"100%",
                        height:"600px"
                    }
                }
            },
            keyMap:{
                type:Object,
                default(){
                    return {
                        "Ctrl-S":(cm)=>{
                            this.$emit("save",this.getData())
                        }
                    }
                }
            }
        },
        computed:{
            config(){
                return {
                    // placeholder:this.placeholder,
                    theme:this.theme.editor,
                    editorTheme:this.theme.editorTheme,
                    previewTheme:this.theme.previewTheme,
                    height: this.size.height,
                    width:this.size.width,
                    path: '/static/plug/editor.md/lib/', 
                    codeFold: true,
                    saveHTMLToTextarea: true,
                    searchReplace: true,
                    htmlDecode: 'style,script,iframe|on*',
                    emoji: true,
                    taskList: true,
                    tocm: true,                  
                    tex: true,                   
                    flowChart: true,            
                    sequenceDiagram: true,
                    tex:true,   
                    toolbarIcons :()=>{
                        return this.tooBars
                    },
                    toolbarCustomIcons : {
                        file: `
                            <label for='file-input' class='file-input-label' title='插入图片'>
                                <i class='fa fa-picture-o' name='image' unselectable='on'></i>
                            </label>
                            <input id='file-input' type='file' ref='fileInput' style='display:none'/>
                        `,
                    },
                    onload:()=>{
                        $("#file-input").bind("change",(e)=>{
                            this.uploadImg(e.target.files[0])
                            e.target.value=""
                        })
                        this.initEditorAfter()
                    }
                }
            }
        },
        data() {
            return {
                Editor: null
            };
        },
        watch:{
            value(val){
                this.value=val
            }
        },
        methods:{
            /**
             * 1.加载editorMd依赖
             * 2.初始化编辑器
             */
            loadJsLib(){
                var rootPath="/static/plug/"
                // this.loadJs([rootPath+"jquery/jquery.min.js",rootPath+"/jquery/zepto.min.js"]).then(()=>{
                //     this.loadJs([rootPath+"editor.md/editormd.min.js"]).then(()=>{
                //         this.initEditor()
                //     })
                // })
                var _self=this
                $script([rootPath+'jquery/jquery.min.js',rootPath+'jquery/zepto.min.js'],"jquery")
                $script.ready('jquery',()=>{
                    $script(rootPath+"editor.md/editormd.min.js",function(){
                        _self.initEditor()
                    })
                })
            },
            // js动态加载器
            // loadJs(path){
            //     return new Promise((resolve,reject)=>{
            //         $script(path,()=>{
            //             resolve()
            //         })
            //     })
            // },
            /**
             * 1、初始化编辑器
             * 2、绑定change事件
             * 3、绑定快捷键
             * @return {[type]} [description]
             */
            initEditor(){
                this.Editor=editormd("editor",this.config)
            },
            /**
             * [initEditorAfter 编辑器初始化完毕后回调函数]
             * @return {[type]} [description]
             */
            initEditorAfter(){
                this.Editor.on("change",(e)=>{
                    this.$emit("change",this.getData())
                })
                this.bindKeyMap(this.keyMap)
            },
            /**
             * [getData 获取编辑器生成的内容]
             * @return {[Object]} [生成的内容]
             */
            getData(){
                let HTML=this.Editor.getPreviewedHTML()
                let MARKDOWN=this.Editor.getMarkdown()
                return {
                    html:HTML,
                    markdown:MARKDOWN
                }
            },
            /**
             * [uploadImg 图片上传]
             * @param  {[Object]} file [文件对象]
             * 1、js处理文件上传
             * 2、上传完成后将图片按照格式插入光标指定位子
             */
            uploadImg(file){
                this.$emit("upload",file)
                // this.Editor.cm.replaceSelection()
            },
            /**
             * [change 监听用户输入数据]
             * @param  {[Object]} data [生成的html内容和markdown源码]
             */
            change(data){
                this.$emit("data",data)
                 this.$emit("changeContext",data.markdown)
                // this.$emit("data",dat)
              
            },
            /**
             * [insert 插入或替换光标指定位置内容]
             * @param  {[String]} data [所要替换的内容字符串]
             */
            insert(data){
                this.Editor.cm.replaceSelection(data)
            },
            /**
             * [bindKeyMap 绑定自定义快捷键]
             * @param  {[Object]} keyMap [description]
             * @return {[type]}        [description]
             */
            bindKeyMap(keyMap){
                this.Editor.addKeyMap(keyMap)
            }
        },
        mounted() {
            this.loadJsLib()
        }
    }
</script>
<style>
    .editormd-textarea{
        display: none;
    }
    .file-input-label{
        cursor: pointer;
        outline: 0;
        color: #666;
        display: inline-block;
        min-width: 24px;
        font-size: 16px;
        text-decoration: none;
        text-align: center;
        -webkit-border-radius: 2px;
        -moz-border-radius: 2px;
        -ms-border-radius: 2px;
        -o-border-radius: 2px;
        border-radius: 2px;
        border: 1px solid #fff;
    }
    .file-input-label:hover{
        border: 1px solid #ddd;
        background: #eee;
    }
</style>