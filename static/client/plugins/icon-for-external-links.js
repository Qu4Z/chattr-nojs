'use strict';
(function() {
  var css = document.createElement('style');
  css.type = 'text/css';
  css.appendChild(document.createTextNode(
    'a[href*="//"]:not([href*="' + location.domain + '"])::after {' +
    'content: url(https://upload.wikimedia.org/wikipedia/commons/6/64/Icon_External_Link.png);' +
    ' margin: 0 2px;}'
  ));
  document.getElementsByTagName('head')[0].appendChild(css);
})();
