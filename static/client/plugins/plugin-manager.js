'use strict';

(function() {

  var plugins_enabled = JSON.parse(localStorage.getItem('plugins') || '[]');
  var plugins_available = JSON.parse(localStorage.getItem('plugins_available') || '[]');

  if (plugins_available.length <= 1) {
    [
      'icon-for-external-links.js',
      'inline-images.js',
      'keep-plugin-manager-open.js',
      'linkify-urls.js'
    ].forEach(function(url) {
      url = '../../s/plugins/' + url;
      if (plugins_available.includes(url)) return;
      plugins_available.push(url);
    });
  }

  function save_plugin_state() {
    // filter duplicates from plugins_enabled and plugins_available.
    function uniq(a) {
      return Array.from(new Set(a));
    }
    plugins_enabled = uniq(plugins_enabled);
    plugins_available = uniq(plugins_available);

    plugins_enabled.forEach(function(url) {
      if (!plugins_available.includes(url)) {
        plugins_available.push(url);
      }
    });

    localStorage.setItem('plugins', JSON.stringify(plugins_enabled));
    localStorage.setItem('plugins_available', JSON.stringify(plugins_available));
  }

  var manager = document.body.insertBefore(document.createElement('div'), document.getElementById('wrapper'));
  manager.id = 'plugin_manager';

  var title = manager.appendChild(document.createElement('p'));
  title.appendChild(document.createTextNode('Plugin Manager'));
  var openclose = title.appendChild(document.createElement('input'));
  openclose.type = 'button';
  title.addEventListener('click', function() {
    var state = manager.classList.toggle('hidden');
    openclose.value = state ? '>>' : '<<';
  });
  openclose.click();

  var ul = manager.appendChild(document.createElement('ul'));
  var top_li = ul.appendChild(document.createElement('li'));
  var input_url = top_li.appendChild(document.createElement('input'));
  input_url.type = 'url';
  input_url.placeholder = 'Plugin URL';
  var input_add = top_li.appendChild(document.createElement('input'));
  input_add.type = 'button';
  input_add.value = 'Add';
  input_add.addEventListener('click', function() {
    if (!input_url.value || !input_url.checkValidity()) {
      input_url.focus();
      return;
    }
    var url = input_url.value;
    input_url.value = '';
    if (plugins_available.includes(url)) {
      return;
    }
    plugins_available.push(url);
    save_plugin_state();
    add_plugin(url);
  });

  function add_plugin(url, enabled) {
    var li = ul.appendChild(document.createElement('li'));
    li.classList.toggle('active', !!enabled);
    var label = li.appendChild(document.createElement('label'));
    var input = label.appendChild(document.createElement('input'));
    var title = url.split('/').reverse()[0];
    title = title.replace(/\.js$/i, '');
    title = title.replace(/\W/g, ' ');
    title = title.replace(/\s+/g, ' ');
    label.appendChild(document.createTextNode(title));
    label.title = url;
    input.type = 'checkbox';
    input.value = url;
    input.checked = !!enabled;
    input.addEventListener('change', plugin_state_toggle);
    close = li.appendChild(document.createElement('input'));
    close.type = 'button';
    close.value = '[x]';
    close.addEventListener('click', function() {
      plugins_available = plugins_available.filter(function(aURL) { return aURL != url;});
      save_plugin_state();
      ul.removeChild(li);
    });
  }

  function plugin_state_toggle(e) {
    var input = e.target;
    var url = input.value;
    if (input.checked) {
      plugins_enabled.push(url);
      save_plugin_state();
      load_plugin(url);
    } else {
      plugins_enabled = plugins_enabled.filter(function(aURL) { return aURL != url;});
      save_plugin_state();
      location.reload();
    }
    input.parentNode.parentNode.classList.toggle('active', input.checked);
  }

  plugins_enabled.forEach(function(url) {
    add_plugin(url, true);
  });

  plugins_available.forEach(function(url) {
    if (plugins_enabled.includes(url)) {
      return;
    }
    add_plugin(url);
  });

  var css = document.createElement('style');
  css.type = 'text/css';
  css.appendChild(document.createTextNode(
    ' #plugin_manager {' +
    '   border: #888 1px solid;' +
    '   float: right;' +
    '   padding: 0 0.5em;' +
    ' }' +
    ' #plugin_manager p, #plugin_manager p input {' +
    '   cursor: pointer;' +
    '   text-align: right;' +
    ' }' +
    ' #plugin_manager.hidden ul {' +
    '   display: none;' +
    ' }' +
    ' #plugin_manager li.active input[type="button"] {' +
    '   display: none;' +
    ' }' +
    ' #plugin_manager input {' +
    '   margin: 0 0.2em;' +
    ' }'
  ));
  document.getElementsByTagName('head')[0].appendChild(css);

})();
