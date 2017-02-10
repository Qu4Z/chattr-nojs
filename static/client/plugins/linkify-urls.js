'use strict';
(function() {
  message_filters.push(function(msg) {
    if (msg.msg.match(/https?:\/\//i)) {
      msg.msg = msg.msg.replace(/([ >]|^)(https?:\/\/[^ <]+)(?=$|[ <])/ig, function(match, d1, url) {
        return d1 + '<a href="' + url + '" target=_blank>' + url + '</a>';
      });
    }
    return msg;
  });
})();
