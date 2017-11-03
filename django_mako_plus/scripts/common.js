(function() {    
    if (window.DMP_CONTEXT === undefined) {
        window["DMP_CONTEXT"] = {
            
            /* Adds data to the DMP context under the given key */
            setContext: function(contextid, data) {
                DMP_CONTEXT[contextid] = data;
            },//addContext

            /* Adds a <script> element dynamically, which ensures the fetched script has document.currentScript (see docs) */
            addScript: function(uid, contextid, src, async) {
                var n = document.createElement("script");
                n.id = uid;
                n.async = async;
                n.setAttribute("data-context", contextid);
                n.src = src;
                // try to add immediately after this script's tag, with fallback to <head>
                if (document.currentScript) {
                    document.currentScript.parentNode.insertBefore(n, document.currentScript.nextSibling);
                }else{
                    document.head.appendChild(n);
                }
            },//addScript

        };//DMP_CONTEXT
    }//if
})()