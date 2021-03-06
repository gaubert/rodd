
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
         * Format product data to be column viewed
         * @param data. The product data to format
         * @return a map containing the data
         */
        column_view_format_product_data:function(data){
            
                var result = {};
                _.each(data.products, function(product) {
                
                     var item = {};
                
                     // iter over distribution for this product
                     _.each(product.distribution, function(dist){
                            
                         // iter over each file elem
                         _.each(product[dist].files, function(file){
                                    
                                var serv_dirs = {};
                                
                                // iter over serv dirs
                                _.each(file.service_dir, function(serv_name) {
                                    serv_dirs[serv_name] = {};
                                });
                                  
                                var i_dist      = {};
                                i_dist[dist]    = serv_dirs;  
                                item[file.name] = i_dist;
                                });
                    
                    result[product.name] = item;
                    
                    });               
               });
               
               return result;
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
         * Format product data
         * @param data. The product data to format
         * @param cols. The colums to display
         * @return map { "cols" : cols_val, rows : rows_val }
         */
        format_accordion_product_data:function(data, cols){
            
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
                                               
                                               // add first line
                                               dummy_list.push('<img src="/static/images/expand-icon.png">');
                
                                              // add all columns within an array for each line
                                              _.each(cols, function(col) { 
                                                                           if (col == "distribution")
                                                                           {
                                                                              // add booleans for distribution info                                                                   
                                                                              dummy_list.push( (_.include(elem[col],"eumetcast-info"))?"Y":"N");
                                                                              dummy_list.push( (_.include(elem[col],"gts-info"))?"Y":"N");
                                                                              dummy_list.push( (_.include(elem[col],"datacentre-info"))?"Y":"N");
                                                                           } 
                                                                           else if (col != "")
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
         * FormatDetails
         */
        format_details:function (oTable, nTr, tableid) {
             
             ///product/$prod_uid/files
             // get data from current lines
             var uid = oTable.fnGetData(nTr)[2];
             
             //alert("hello " + uid);
             var to_print = "";
             
             $.ajaxSetup({async:false});
             $.getJSON("/product/"+uid+"/files",
                      {},
                      function(data) {
                         
                         _.each(data['files'], function(file) {
                             to_print += file['regexpr'] + " in " + file['dis_type'] + "</br>"
                         });
                     
                      });
             $.ajaxSetup({async:true});
             
             return to_print; 
         },
		
		/**
         * create a table with accordion from the passed data using dataTable jquery plugin
         *
         *  @param  data a Map with cols and rows values
         *  @return void
         */ 
        render_accordion_table:function(table_name, data){
            
            // check that the data is a map 
            
            var cols = data.cols;
            var rows = data.rows;
            
            var anOpen = []; //to keep track of open pages
          
            //Change table title in tablename
            $('#tblname').text(table_name);
            $('#titlename').text(table_name);
            
            // remove waiting images
            $('#waitimg').empty();
            $('#bigwaitimg').empty();
                     
            var oTable = $('#rodd_table').dataTable( {
                   // enable the JQueryUI Theme Roller
                   "bJQueryUI": true,
                   // change pagination in full_number mode
                   "sPaginationType": "full_numbers",
                   // save users preferences
                   "bStateSave": true,
                   // change defaults for pagination value
                   "aLengthMenu": [[25, 50, 100, -1], [25, 50, 100, "All"]],
                   "aoColumnDefs": [ { "sClass": "control", "aTargets": [ 0 ] }],
                   "aaData"    : rows,
                   "aoColumns" : cols,
             });

             var fixheader = new FixedHeader( oTable );
             
             $('#rodd_table td.control').live('click', function () {
                    var nTr = this.parentNode;
                    var i = $.inArray(nTr, anOpen);

                    if (i === -1) {
                        $('img', this).attr('src', "/static/images/minimize-icon.png");
                        var nDetailsRow = oTable.fnOpen(nTr, rodd.format_details(oTable, nTr, 2), 'details');
                        
                        // effect is not working to be defined
                        /*$('div.innerDetails', nDetailsRow).slideDown('fast', function () {
                            $("div.dataTables_scrollBody").scrollTop(nTr.offsetTop);
                        });*/
                        
                        anOpen.push(nTr);
                        
                    }
                    else {
                        $('img', this).attr('src', "/static/images/expand-icon.png");
                        oTable.fnClose(nTr);
                        anOpen.splice(i, 1);
                        
                        
                        /*$('div.innerDetails', $(nTr).next()[0]).slideUp(function () {
                            oTable.fnClose(nTr);
                            anOpen.splice(i, 1);
                        });*/
                    }
             });
             
             
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
            
            // remove waiting images
            $('#waitimg').empty();
            $('#bigwaitimg').empty();
                     
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
             
		}
	};
	
	
	if(!window.rodd){window.rodd=rodd;}//We create a shortcut for our framework, we can call the methods by $$.method();
	
	
})(jQuery,_);
