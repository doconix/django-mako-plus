(function() {    
    if (window.DMP_CONTEXT === undefined) {
        
        window.DMP_CONTEXT = {
            
            /* A check for the dmp version so we don't have mismatches */
            __version__: '4.3.2',
            
            /* Adds data to the DMP context under the given key */
            set: function(version, contextid, data) {
                if (DMP_CONTEXT.__version__ != version) {
                    console.warn('DMP framework version is ' + version + ' dmp-common.js is ' + DMP_CONTEXT.__version__ + '. Unexpected behavior may occur.');
                }
                DMP_CONTEXT[contextid] = data;
            },
            
            /* 
                Retrieves context data.  Usage:
            
                    DMP_CONTEXT.get()                                           // for the currently-executing script
                    DMP_CONTEXT.get('myapp/mytemplate')                         // for the app/template
                    DMP_CONTEXT.get(document.querySelector('some selector'))    // for the specified <script> tag
            */
            get: function(option) {
                // default to currentScript if undefined
                if (option === undefined) {  
                    if (document.currentScript === undefined) {
                        throw Error('document.currentScript is undefined. DMP_CONTEXT.get() can only be done during initial script processing (not in callbacks or event handling).');
                    }
                    return DMP_CONTEXT[document.currentScript.getAttribute('data-context')];
                }  
                
                // <script> tag
                if (option.nodeType === 1 && option.nodeName.toLowerCase() == 'script') {
                    return DMP_CONTEXT[option.getAttribute('data-context')];
                }//if
                
                // "app/template"
                var elem = document.querySelector('script[data-template="' + option + '"]');
                if (!elem) {
                    throw Error('DMP_CONTEXT.get() could not find a <script> with data-template="' + option + '".');
                }
                return DMP_CONTEXT[elem.getAttribute('data-context')];
            },
            
            /* Adds a <script> element dynamically, which ensures the fetched script has document.currentScript (see docs) */
            addScript: function(uid, contextid, template, src, async) {
                var n = document.createElement("script");
                n.id = uid;
                n.async = async;
                n.setAttribute('data-template', template);
                n.setAttribute("data-context", contextid);
                n.src = src;
                // try to add immediately after this script's tag, with fallback to <head>
                if (document.currentScript) {
                    document.currentScript.parentNode.insertBefore(n, document.currentScript.nextSibling);
                }else{
                    document.head.appendChild(n);
                }
            },

        };//DMP_CONTEXT
        
    }//if
})()