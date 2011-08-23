<script type=text/javascript src="http://ajax.googleapis.com/ajax/libs/jquery/1.4.2/jquery.min.js"></script>
<script type=text/javascript>
  //$SCRIPT_ROOT = {{ request.script_root|tojson|safe }};
  $SCRIPT_ROOT = 'localhost:5000';
</script>

<script type=text/javascript>
  $(function() {
    $('a#calculate').bind('click', function() {
      $("#result").text(42);
   
      var img = $('#ex2').get()[0].src;
      console.log("img = " + img);
      if (img == 'file:///homespace/gaubert/bottle-logo.png')
      {
        console.log("In flask");
        $('#ex2').get()[0].src = '/homespace/gaubert/flask.png';
      }
      else
      { 
        console.log("In bottle");
        $('#ex2').get()[0].src = '/homespace/gaubert/bottle-logo.png';
      }
      
      });
      
      return false;
    });
</script>
<h1>jQuery Example</h1>
<p><input type=text size=5 name=a> +
   <input type=text size=5 name=b> =
   <span id=result>?</span>
<p><a href=# id=calculate>calculate server side</a>
<img id='ex2' src="/homespace/gaubert/flask.png" />
