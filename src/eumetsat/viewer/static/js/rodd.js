
/**
 * First version of the rodd library (not plugable for the moment)
 */
(function($){
	
	var rodd = {
		
		hello:function(){
			alert("hello");
		},	
		
		
		/**
		 * Format data genericly
		 * @param data. The data to format
		 * @param cols. The colums to display
		 */
		format_channel_data_generic:function(data, cols){
			// format the data to feed data tables
		    if (data.channels.length <= 0 )
		    {
		        alert("No Channels returned");
		    } 
		    else
		    {
		        var channels = data.channels;
		        var aaData = [];
		        // prepare data
		        var dummy_list;
		        for(var i=0, len = data.channels.length; i < len; i++)
		        {
		           dummy_list = [];
		           for (var j=0, len_j = cols.length; j<len_j; j++)
		           {
				     dummy_list.push(channels[i][cols[j]]);
				   }
				   aaData.push(dummy_list);
			    }
			    
			    /*var aoColumns = [];
			    for (var k=0,len_k=cols.length;k<len_k; k++)
			    {
                    aoColumns.push({ "sTitle" : cols[k] });
			    }*/
			    var aoColumns = [
                    { "sTitle": "Name" },
                    { "sTitle": "Multicast_Address" },
                    { "sTitle": "Function" },
                    { "sTitle": "Min Rate"},
                    { "sTitle" : "Max Rate"}
                ];
			    
			    return { "cols" : aoColumns,
			             "rows" : aaData
			           };
			             
		    }
			
		},    
		
		format_channel_data:function(data){
			
		    // format the data to feed data tables
		    if (data.channels.length <= 0 )
		    {
		      alert("No Channels returned");
		    } 
		    else
		    {
		    
		      var channels = data.channels;
		      var aaData = [];
		    
		      for(var i=0, len = data.channels.length; i < len; i++)
		      {
				//console.log("Name:" + channels[i].name);
				aaData.push([ channels[i].name, channels[i].multicast_address, channels[i].channel_function, channels[i].min_rate, channels[i].max_rate ]);
			  }
			  
			  var aoColumns = [
					{ "sTitle": "Name" },
					{ "sTitle": "Multicast_Address" },
					{ "sTitle": "Function" },
					{ "sTitle": "Min Rate"},
					{ "sTitle" : "Max Rate"}
                ];
             
                
                return { "cols" : aoColumns, 
                         "rows" : aaData
                       };
                
		    }
		},
		
		/**
         * Render the passed data map(cols,rows)
         *
         * @return void
         */ 
		render_data:function(table_name, data){
			
			// check that the data is a map 
			
			var cols = data.cols;
			var rows = data.rows;
			
			//Change table title in tablename
            $('#tblname').text(table_name);
                     
            var oTable = $('#example').dataTable( {
                   // enable the JQueryUI Theme Roller
	               "bJQueryUI": true,
	               // change pagination in full_number mode
	               "sPaginationType": "full_numbers",
	               // save users preferences
	               "bStateSave": true,
	               // change defaults for pagination value
	               "aLengthMenu": [[25, 50, 100, -1], [25, 50, 100, "All"]],
				   "aaData"    : rows,
				   "aoColumns" : cols
             });

             var fixheader = new FixedHeader( oTable );	
		}
	};
	
	
	if(!window.rodd){window.rodd=rodd;}//We create a shortcut for our framework, we can call the methods by $$.method();
	
	
})(jQuery);