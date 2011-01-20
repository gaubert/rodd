<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01//EN" "http://www.w3.org/TR/html4/strict.dtd">
<html>
    <head>
        <meta http-equiv="content-type" content="text/html; charset=utf-8" />
        
        <title>{{table}} table</title>
        <style type="text/css" title="currentStyle">
            @import "/static/css/rodd_page.css";
            @import "/static/css/rodd_table.css";
            @import "/static/themes/eumetsat-theme/jquery-ui-1.8.4.custom.css";
        </style>
        <!-- <script type="text/javascript" language="javascript" src="http://ajax.googleapis.com/ajax/libs/jquery/1.4.2/jquery.min.js"></script> -->
        <script type="text/javascript" language="javascript" src="/static/js/jquery.js"></script> 
        <script type="text/javascript" language="javascript" src="/static/js/underscore-min.js"></script>
        <script type="text/javascript" language="javascript" src="/static/js/jquery.dataTables.min.js"></script>
        <script type="text/javascript" language="javascript" src="/static/js/FixedHeader.min.js"></script>
        <script type="text/javascript" language="javascript" src="/static/js/rodd.js"></script>
        <script type="text/javascript" charset="utf-8">
            $(document).ready(function() {
                $.getJSON("{{data_url}}",
                      {},
                      function(data) {
                         var col_names = [ "name", "multicast_address", "channel_function", "min_rate", "max_rate" ];
                         rodd.render_table({{page_name}}, rodd.format_data(data, col_names));
                      }
                )
            });
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
                       <span class="flickspan"><a href="/static/view_channels.html">Channels</a></span>
                       <span class="flickspan"><a href="/families">Families</a></span>
                       <span class="flickspan"><a href="/products_2_servdirs">Products2ServiceDirs</a></span>
                       <span class="flickspan"><a href="/servdirs_2_families">ServiceDirs2Families</a></span>
                </td>
              </tr>
            </table>
            
            <h1 id="tblname">Unknown Table</h1>
            <p>Table accessed with the RODD viewer</p>
            <div id="demo">
            <table cellpadding="0" cellspacing="0" border="0" class="display" id="rodd_table"></table>
            </div>
            
           <div class="spacer"></div>
      </div>
   </body>
