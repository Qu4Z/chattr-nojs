'use strict';
(function() {
  message_filters.push(function(msg) {
    if (msg.msg.match(/https?:\/\//i)) {
      msg.msg = msg.msg.replace(/([ >]|^)(https?:\/\/[^ <]+)(?=$|[ <])/ig, function(match, d1, url) {
        if (url.match(/\.(gif|jpe?g|png|bmp|tga|ico|webp|tiff?)(\?[^?]+)?$/i)) {
          return d1 + '<img class="auto-inline" src="' + url + '" alt="' + url + '">';
        }
        return match;
      });
    }
    return msg;
  });

  var css = document.createElement('style');
  css.type = 'text/css';
  css.appendChild(document.createTextNode(
    '.auto-inline{max-width:100%; max-height:600px;}'
  ));
  document.getElementsByTagName('head')[0].appendChild(css);
})();
