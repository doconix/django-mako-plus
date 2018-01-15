// note that I'm intentionally using older JS syntax to meet 
// the widest possible browser base

(function() {    
    if (window.DMP_CONTEXT === undefined) {
        
        window.DMP_CONTEXT = {
            
            __version__: '4.5.5',   // DMP version to check for mismatches
            contexts: {},           // contextid -> context1
            contextsByName: {},     // app/template -> [ context1, context2, ... ]
            
            /* Adds data to the DMP context under the given key */
            set: function(version, contextid, data) {
                if (DMP_CONTEXT.__version__ != version) {
                    console.warn('DMP framework version is ' + version + ', while dmp-common.js is ' + DMP_CONTEXT.__version__ + '. Unexpected behavior may occur.');
                }
                DMP_CONTEXT.contexts[contextid] = data;
            },    
            
            /* Links a template to its context id */
            linkContextByName(contextid, template) {
                if (DMP_CONTEXT.contextsByName[template] === undefined) {
                    DMP_CONTEXT.contextsByName[template] = [];
                }
                DMP_CONTEXT.contextsByName[template].push(contextid);
            },

            /* Adds a <script> element dynamically, which ensures the fetched script has document.currentScript (see docs) */
            addScript: function(uid, contextid, template, src, async) {
                // <script> element
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
            
            /* 
                Retrieves context data. If multiple script contexts are found, such as when ajax retrieves
                the same template snippet multiple times, the last one is returned.
            
                    DMP_CONTEXT.get()                                           // for the currently-executing script
                    DMP_CONTEXT.get('myapp/mytemplate')                         // for the app/template
                    DMP_CONTEXT.get(document.querySelector('some selector'))    // for the specified <script> tag
            */
            get: function(option) {
                var ret = DMP_CONTEXT.getAll(option);
                if (ret.length == 0) {
                    return undefined;
                }
                return ret[ret.length - 1];
            },
            
            /*
                Retrieves the context data for all scripts on the page matching the option.
                The returned array usually has one context item.  But when ajax retrieves the same
                template snippet multiple times, it will have multiple contexts in the array.
            
                    DMP_CONTEXT.getAll()                        // an array of one item: currently-executing script
                                                                // (this is the preferred way when on script's first execution)
                    DMP_CONTEXT.getAll(elem)                    // an array of one item: context for the given <script> element
                                                                // (elem retrieved with querySelector, getElementById, etc.)
                    DMP_CONTEXT.getAll('myapp/mytemplate')      // an array of all scripts matching this template name
            */
            getAll: function(option) {
                var ret = [];
                
                // default to currentScript if undefined
                if (option === undefined || option === null) {  
                    if (document.currentScript === undefined) {
                        throw Error('document.currentScript is undefined. DMP_CONTEXT.get() can only be done during initial script processing (not in callbacks or event handling).');
                    }
                    option = document.currentScript;
                }  
                
                // if still undefined, we can't pull anything
                if (option === undefined || option === null) {  
                    return ret;
                }
                
                // "app/template"
                if (typeof option === 'string' || option instanceof String) {
                    var namemap = DMP_CONTEXT.contextsByName[option];
                    if (namemap !== undefined) {
                        for (var i = 0; i < namemap.length; i++) {
                            var c = DMP_CONTEXT.contexts[namemap[i]];
                            if (c !== undefined) {
                                ret.push(c);
                            }
                        }
                    }
                }
                
                // script element
                else if (option.nodeType === 1 && option.nodeName.toLowerCase() == 'script') {
                    var c = DMP_CONTEXT.contexts[option.getAttribute('data-context')];
                    if (c !== undefined) {
                        ret.push(c);
                    }
                }//if
                
                return ret;
            },
            
        };//DMP_CONTEXT
        
    }//if
})()