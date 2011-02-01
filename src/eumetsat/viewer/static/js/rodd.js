
/**
 * First version of the rodd library (not plugable for the moment)
 * @param jquery 
 * @param underscore
 */
(function($,_){
	
	var rodd = {
		
		hello:function(){
			alert("hello");
		},	
		
		/**
         * Format product data
         * @param data. The product data to format
         * @param cols. The colums to display
         * @return map { "cols" : cols_val, rows : rows_val }
         */
        format_product_data:function(data, cols){
        	
        	// format the data to feed data tables
            if (data.length <= 0 )
            {
                alert("No data lines returned");
            }
            else
            {
                var aaData = [];
                // prepare data
                var dummy_list;
                
                // process eachline
                _.each(data, function(elem) { dummy_list = []; 
	                                          // add all columns within an array for each line
	                                          _.each(cols, function(col) { 
	                                          	                           if (col == "distribution")
	                                          	                           {
	                                          	                           	  // add booleans for distribution info                                  	                           	  
	                                          	                           	  dummy_list.push( (_.include(elem[col],"eumetcast-info"))?"Y":"N");
	                                          	                           	  dummy_list.push( (_.include(elem[col],"gts-info"))?"Y":"N");
	                                          	                           	  dummy_list.push( (_.include(elem[col],"datacentre-info"))?"Y":"N");
	                                          	                           } 
	                                          	                           else
	                                          	                           {
	                                          	                              dummy_list.push(elem[col]);
	                                          	                           }
	                                          	                         });
	                                          aaData.push(dummy_list); 
                                      });
                
                var aoColumns = [];
                _.each(cols, function(col) { 
                	                          // exception for distribution
                	                          if (col == "distribution")
                	                          {
                	                          	 // add distribution columns
                	                          	 aoColumns = aoColumns.concat([ { "sTitle" : "Eumetcast"}, { "sTitle":"Gts"}, { "sTitle": "Data Centre"}]);
                	                          }
                	                          else
                	                          {
                	                             aoColumns.push( { "sTitle" : col } );
                	                          } 
                	                       });
                
                return { "cols" : aoColumns,
                         "rows" : aaData
                       };
                         
            }
        },
		
		
		/**
		 * Format data genericly
		 * @param data. The data to format
		 * @param cols. The colums to display
		 * @return map { "cols" : cols_val, rows : rows_val }
		 */
		format_data:function(data, cols){
			// format the data to feed data tables
		    if (data.length <= 0 )
		    {
		        alert("No data lines returned");
		    } 
		    else
		    {
		        var aaData = [];
		        // prepare data
		        var dummy_list;
		        
		        // process eachline
		        _.each(data, function(elem) { dummy_list = []; 
	                                          // add all columns within an array for each line
	                                          _.each(cols, function(col) { dummy_list.push(elem[col]); });
	                                          aaData.push(dummy_list); 
		                              });
			    
			    var aoColumns = [];
			    _.each(cols, function(col) { aoColumns.push( { "sTitle": col } ); });
			    
			    return { "cols" : aoColumns,
			             "rows" : aaData
			           };
			             
		    }
			
		},    
		
		/**
         * create a table from the passed data using dataTable jquery plugin
         *
         *  @param  data a Map with cols and rows values
         *  @return void
         */ 
		render_table:function(table_name, data){
			
			// check that the data is a map 
			
			var cols = data.cols;
			var rows = data.rows;
			
			//Change table title in tablename
            $('#tblname').text(table_name);
            $('#titlename').text(table_name);
                     
            var oTable = $('#rodd_table').dataTable( {
                   // enable the JQueryUI Theme Roller
	               "bJQueryUI": true,
	               // change pagination in full_number mode
	               "sPaginationType": "full_numbers",
	               // save users preferences
	               "bStateSave": true,
	               // change defaults for pagination value
	               "aLengthMenu": [[25, 50, 100, -1], [25, 50, 100, "All"]],
				   "aaData"    : rows,
				   "aoColumns" : cols,
             });

             var fixheader = new FixedHeader( oTable );
             
             $('#rodd_table tbody tr td:eq(2)').each( function() {
			        var sTitle;
			        //var nTds = $('td', this);
			        //var sEum = $(nTds[2]).text();
			        var sEum = this.textContent;
			        
			        if ( sEum == "Y" )
			            sTitle =  'On Eumetcast';
			        else 
			            sTitle =  'Not On Eumetcast';
			        
			        this.setAttribute( 'title', sTitle );
            } );
    
            /* Apply the tooltips not working at the moment */
            /*$('#rodd_table tbody td[title]').tooltip( {
                "delay": 0,
                "track": true,
                "fade": 250,
            } );*/
            
            //
            $('#waitimg').empty();
             
		}
	};
	
	
	if(!window.rodd){window.rodd=rodd;}//We create a shortcut for our framework, we can call the methods by $$.method();
	
	
})(jQuery,_);
