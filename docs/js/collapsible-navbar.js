String.prototype.format = function() {
  a = this;
  for (k in arguments) {
    a = a.replace("{" + k + "}", arguments[k])
  }
  return a
}

$(document).ready(function () {
  $('li.toctree-l1').each(function () {
    var parent = $(this);
    var a      = parent.find('a:first');
    var next   = null;
    $('li.toctree-l1').each(function() {
      var span = $(this).find('span:first');
      if (a.text() != '' && a.text() == span.text()) {
        span.remove();
        next = $(this);
        return false
      }
    });
    if (next !== null) {
      var ul = next.find('ul.subnav:not(li.toctree-l2)');
      next.prepend(a);
      if ($(this).hasClass('current')) next.addClass('current');
      var new_a = '<a class="fa fa-caret-{0} collapse-navbar" href="#" style="display: inline-block; position: absolute; width: auto; right: 0; margin-right: 2px; padding-left: 2px; padding-right: 2px; z-index: 1001;"></a>';
      if (!ul.children('li.current').length) {
        ul.hide();
        $(new_a.format("left")).insertBefore(a);
      } else {
        $(new_a.format("down")).insertBefore(a);
      }
      $(this).remove();
    }
  });
  $('a.collapse-navbar').click(function () {
    var parent = $(this).closest('li.toctree-l1');
    var subnav = parent.find('ul.subnav:not(li.toctree-l2)');
    if ($(this).hasClass('fa-caret-left')) {
      subnav.show();
      $(this).removeClass('fa-caret-left');
      $(this).addClass('fa-caret-down');
    } else {
      subnav.hide();
      $(this).addClass('fa-caret-left');
      $(this).removeClass('fa-caret-down');
    }
});});
