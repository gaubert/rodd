/**
 * First version of the rodd library (not plugable for the moment)
 * @param jquery 
 * @param underscore
 */
(function($,_){
    
    var methods = {
        columnview: null,
        options: null,
        is_int: function(s) {
            return (s.toString().search(/^-?[0-9]+$/) === 0);
        },
        get_num: function(node) {
            return parseInt(node.data('num'));//make sure this is an integer
        },
        inc_num: function(node) {
            node.data('num', methods.get_num(node)+1);
            return methods.get_num(node);
        },
        dec_num: function(node) {
            node.data('num', methods.get_num(node)-1);
            return methods.get_num(node);
        },
        
        get_data_to_display:function(path) {
            var columnview = methods.columnview;
            var data_to_display = columnview.data('data');
            
            var val = data_to_display;
        
            if (path.length > 0)
            {
              _.each(path, function(key) { val = val[key]; }); //iterate over each key to go to the right values
            }
         
            return val;
        },
        // transform a path array in a string
        path_to_string:function(path){
            var str_path = '';
            
            _.each(path, function(key, index) { 
                      if (index === 0)
                      {
                          str_path += key;                     
                      }
                      else
                      {
                          str_path += ',' + key;
                      }
            });
            return str_path;
        },
        // transform a stringified path into an array
        string_to_path:function(str)
        {
            var path = [];
            _.each(str.split(','), function (elem) { path.push(elem); } );
            return path;
        },
        
        // get first element of associative array dara
        get_first_element:function(data) {
            for (var prop in data)
            {
              return prop;
            }
        },
        // reduce the path to the current position
        reduce_path:function(pos) {
            var columnview = methods.columnview;
            
            var path       = columnview.data('path');
            
            if (pos == 1)
            {
                path = [];
            }
            else
            {
               path = _.first(path, pos-1);
            }
                  
            columnview.data('path', path); //update key_list
            
            return path;
        },
       
        expand: function(path, new_position) {
            var columnview = methods.columnview;
            var seek = null;
            
            //Clean the different columns
            columnview.find('.column').each(function() {
                var colnum = methods.get_num($(this));
                if(colnum == new_position) 
                {
                    // current column to be changed is the current one and is already displayed. clean it
                    // seek = $(this);
                    //seek.empty();
                    $(this).remove();
                    methods.dec_num(columnview);
                    
                    
                } 
                else if(colnum > new_position) 
                {
                    // current column is deeper than the one to display. supress it
                    $(this).remove(); //kill leaves that no longer apply to new child
                    methods.dec_num(columnview);
                }
            });
            
            // did not find the column to display so create a new one
            if(!seek) 
            {
                seek = methods.create_column(path);
                if (seek)
                {
                   seek.appendTo(columnview);
                   methods.setup_links(seek);
                   seek.scrollTop(0);
                }
            }
            else
            {
                methods.setup_links(seek);
                seek.scrollTop(0);
            }
            
        },
        // expand from where we are
        expand_columns: function(path, position) {
            
            var last_level = 3 ; // constant that should be moved somewhere else
            var curr_pos   = position;
            
            // get the column view that needs to be populated
            var columnview      = methods.columnview;
            
            var data_to_display = methods.get_data_to_display(path);
            
            while (curr_pos != last_level)
            {
               var div = methods.create_column(path);
               columnview.append(div);
               methods.setup_links(div);
               
               // update the path
               methods.get_data_to_display(path);
               
               path.push(methods.get_first_element(data_to_display));
               
               curr_pos += 1;
               
            }
        },
        create_3level_columns: function(orig_path) {
            // get the column view that needs to be populated
            var columnview      = methods.columnview;
	
            var path = []; // the path that is constructed dynamically
            
            var data_to_display = methods.get_data_to_display(orig_path);
            
            var div1 = methods.create_column(orig_path);
            
            path.push(methods.get_first_element(data_to_display));
            
            var div2 = methods.create_column(path);
            
            path.push(methods.get_first_element(methods.get_data_to_display(path)));
            
            var div3 = methods.create_column(path);
            
            path.push(methods.get_first_element(methods.get_data_to_display(path)));
            
            columnview.append(div1);
            methods.setup_links(div1);
            columnview.append(div2);
            methods.setup_links(div2);
            columnview.append(div3);
            methods.setup_links(div3);	
        },
        
        // remove all columns going further than where we are (position)
        clean_columns: function(position) {
            var columnview      = methods.columnview;

            //Clean the different columns
            columnview.find('.column').each(function() {
                var colnum = methods.get_num($(this));
                if(colnum > position) 
                {
                    // clean columns
                    $(this).remove();
                    methods.dec_num(columnview);      
                } 
            });
        },
        
        
        create_column: function(path) {
            var columnview      = methods.columnview;
            
            var data_to_display = methods.get_data_to_display(path);
            
            // if there is some data to display
            var div = null;
            if (_.size(data_to_display) > 0)
            {
                var num = methods.inc_num(columnview); //next leaf in columns
                
                //div = $('<span class="column" style="float:left;"><ul class="list"></ul></span>');
                div = $('<span class="column"><select class="selector" multiple="multiple"></select></span>');
                //div = $('<select class="column" multiple="multiple"/>');
                
                // always apply the same width for all columns
                div.css('width', 200);
                
                div.data('num', num);
                columnview.data('num', num);
               
                var cpt = 0;
                // for each data line add a <li> tag
                
                _.each(data_to_display, function(val, key) 
                { 
                   // clone path and the key at the end
                   var n_path = _.clone(path);
                   n_path.push(key);
                  
                   if (cpt === 0)
                   {
                      div.find('select').append('<option path="'+ methods.path_to_string(n_path) + '" selected="">'+key+'</option>'); 
                   }
                   else
                   {
                      div.find('select').append('<option path="'+ methods.path_to_string(n_path) + '" >'+key+'</option>');
                   }
                   cpt = cpt + 1;
                });
            }

            return div;
        },
        smart_columns: function() { //Create a function that calculates the smart columns

            //Reset column size to a 100% once view port has been adjusted
		    $("#column").css({ 'width' : "100%"});
		
		    var colWrap = $("ul.column").width(); //Get the width of row
		    var colNum = Math.floor(colWrap / 1000); //Find how many columns of 200px can fit per row / then round it down to a whole number
		    var colFixed = Math.floor(colWrap / colNum); //Get the width of the row and divide it by the number of columns it can fit / then round it down to a whole number. This value will be the exact width of the re-adjusted column
		
		    $("ul.column").css({ 'width' : colWrap}); //Set exact width of row in pixels instead of using % - Prevents cross-browser bugs that appear in certain view port resolutions.
		    $("ul.column li").css({ 'width' : colFixed}); //Set exact width of the re-adjusted column   

        },   
        setup_links: function(column) {
            //column.find('a:not(.ignore-link)').each(function() {
            column.find('option').each(function() {
                $(this).click(function(evt) {
                    
                    var key = $(this).text();   // the key clicked on
                    var position = methods.get_num(column); // the current position
                    
                    //methods.reduce_path(position);
                    
                    var path = methods.string_to_path($(this).attr("path"));
                    
                    // add selected element in path
                    //path.push(key);
                    
                    column.find('a.selected').removeClass('selected').trigger('columnview-deselected');
                   
                    //var url = $(this).attr('href'); // not necessary
                    
                    methods.clean_columns(position);
                    methods.expand_columns(path, position);
                    
                    //methods.expand(path, position+1); //expand into the next column
                    $(this).addClass('selected').trigger('columnview-selected');
                    evt.preventDefault();
                    return false;
                });
            });
        },
        init: function(data, options) {
            methods.options = options;
            var columnview = methods.columnview;
            columnview.data('num', 0); //init column counter
            columnview.data('data', data);//add the data in the dom
            columnview.data('path', []);// list of keys where we are in the data
            methods.create_3level_columns(columnview.data('path'));          
        }
    };
        
    // Add trim in String
    if(typeof(String.prototype.trim) === "undefined")
    {
       String.prototype.trim = function() 
       {
        return String(this).replace(/^\s+|\s+$/g, '');
       };
    }
    
    $.fn.columnview = function(method) {
        methods.columnview = this;

        if ( methods[method] ) {
            return methods[ method ].apply( this, Array.prototype.slice.call( arguments, 1 ));
        } else if ( typeof method === 'object' || ! method ) {
            return methods.init.apply( this, arguments );
        } else {
            $.error( 'Method ' +  method + ' does not exist on jQuery.columnview' );
        } 

        return this;
    };
    
})(jQuery,_);