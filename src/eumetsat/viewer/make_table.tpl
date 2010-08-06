%#template to generate a HTML table from a list of tuples (or list of lists, or tuple of tuples or ...)
<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01//EN" "http://www.w3.org/TR/html4/strict.dtd">
<html>
	<head>
		<meta http-equiv="content-type" content="text/html; charset=utf-8" />
		
		<title>format_type table</title>
		<style type="text/css" title="currentStyle">
			@import "/media/css/demo_page.css";
			@import "/media/css/demo_table.css";
			@import "/media/themes/ui-darkness/jquery-ui-1.8.2.custom.css";
		</style>
		<script type="text/javascript" language="javascript" src="/media/js/jquery.js"></script>
		<script type="text/javascript" language="javascript" src="/media/js/jquery.dataTables.js"></script>
		<script type="text/javascript" charset="utf-8">
			$(document).ready(function() {
				$('#example').dataTable({
				    "bJQueryUI": true,
				    "sPaginationType": "full_numbers",
				    
				});
			} );
		</script>
	</head>
	<body id="dt_example">
		<div id="container">
			<div class="full_width big">
				<i>RODD (Repository of Dissemniation Data)</i></div>
			
			<h1>format_type table</h1>
			<p>First table accessed with the RODD viewer</p>
			<div id="demo">
<table cellpadding="0" cellspacing="0" border="0" class="display" id="example">
 <thead>
   <tr class="gradeA">
     <th>Column NB</th>
	 <th>Format Name</th>
	 <th>Description</th>
   </tr>
 </thead>
 <tbody>
  %for row in rows:
  <tr class="gradeA">
  %for r in row:
    <td>{{r}}</td>
  %end
  </tr>
%end
  </tbody>
</table>
</div>
<div class="spacer"></div>
