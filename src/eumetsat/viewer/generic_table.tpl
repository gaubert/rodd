%#template to generate a HTML table from a list of tuples (or list of lists, or tuple of tuples or ...)
<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01//EN" "http://www.w3.org/TR/html4/strict.dtd">
<html>
	<head>
		<meta http-equiv="content-type" content="text/html; charset=utf-8" />
		
		<title>{{table}} table</title>
		<style type="text/css" title="currentStyle">
			@import "/media/css/rodd_page.css";
			@import "/media/css/rodd_table.css";
			@import "/media/themes/eumetsat-theme/jquery-ui-1.8.4.custom.css";
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
			<div class="flickh1">
				<i>RODD (Repository of Dissemination Data)</i>
			</div>
			<wbr>
			<table cellspacing="0" id="SubNav">
	          <tr>
		         <td class="dt_section">
		            <div class="full_width big"> Your Tables: </div>
			        <p class="LinksNewP">
			         <span class="LinksNew">
			           <span class="flickspan"><a href="/products">Products</a></span>
			           <span class="flickspan"><a href="/service_dirs">ServiceDirs</a></span>
			           <span class="flickspan"><a href="/channels">Channels</a></span>
			           <span class="flickspan"><a href="/products_2_servdirs">Products2ServiceDirs</a></span>
			           <wbr>
			           <span class="photo_navi_contact" id="photo_navi_contact_span_87741494@N00"></span>
			        </p>
		        </td>
		      </tr>
		    </table>
			
			<h1>{{table}} table</h1>
			<p>Table accessed with the RODD viewer</p>
			<div id="demo">
<table cellpadding="0" cellspacing="0" border="0" class="display" id="example">
 <thead>
   <tr class="gradeA">
     %for h in heads:
        <th>{{h}}</th>
     %end
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
