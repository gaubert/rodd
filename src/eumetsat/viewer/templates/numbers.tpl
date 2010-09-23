<script type=text/javascript src="/static/js/jquery.js"></script>
<script type=text/javascript>
  //$SCRIPT_ROOT = {{ request.script_root|tojson|safe }};
  $SCRIPT_ROOT = 'localhost:5000';
</script>

<script type=text/javascript>
  $(function() {
    $('a#calculate').bind('click', function() {
      $.getJSON('http://localhost:5000' + '/count_numbers', {
        a: $('input[name="a"]').val(),
        b: $('input[name="b"]').val()
      }, function(data) {
        $("#result").text(data.result);
      });
      return false;
    });
  });
</script>
<h1>jQuery Example</h1>
<p><input type=text size=5 name=a> +
   <input type=text size=5 name=b> =
   <span id=result>?</span>
<p><a href=# id=calculate>calculate server side</a>
