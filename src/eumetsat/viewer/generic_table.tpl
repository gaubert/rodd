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
		<script type="text/javascript" language="javascript" src="/media/js/jquery.dataTables.min.js"></script>
		<script type="text/javascript" language="javascript" src="/media/js/FixedHeader.min.js"></script>
		<script type="text/javascript" charset="utf-8">
			$(document).ready(function() {
				var oTable = $('#example').dataTable({
				               // enable the JQueryUI Theme Roller
				               "bJQueryUI": true,
				               // change pagination in full_number mode
				               "sPaginationType": "full_numbers",
				               // save users preferences
				               "bStateSave": true,
				               // change defaults for pagination value
				               "aLengthMenu": [[25, 50, 100, -1], [25, 50, 100, "All"]],
				    });
				
				new FixedHeader( oTable );
				
			} );
		</script>
	</head>
	<body id="dt_example">
		<div id="container">
			<div class="flickh1">
				<i>RODD (Repository of Dissemination Data)</i>
			</div>
			<wbr/>
			<table cellspacing="0" id="SubNav">
	          <tr>
		         <td class="dt_section">
		            <div class="full_width big"> Your Tables: </div>
		               <span class="flickspan"><a href="/products_details">Products Details</a></span>
			           <span class="flickspan"><a href="/tbl_products">Products Tbl</a></span>
			           <span class="flickspan"><a href="/service_dirs">ServiceDirs</a></span>
			           <span class="flickspan"><a href="/channels">Channels</a></span>
			           <span class="flickspan"><a href="/families">Families</a></span>
			           <span class="flickspan"><a href="/products_2_servdirs">Products2ServiceDirs</a></span>
			           <span class="flickspan"><a href="/servdirs_2_families">ServiceDirs2Families</a></span>
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
