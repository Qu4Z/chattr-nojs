'use strict';
(function() {
  var css = document.createElement('style');
  css.type = 'text/css';
  css.appendChild(document.createTextNode(
    '#plugin_manager.hidden ul { display: block; } #plugin_manager p { display: none; }'
  ));
  document.getElementsByTagName('head')[0].appendChild(css);
})();
