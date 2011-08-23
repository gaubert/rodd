/**
 * First version of the rodd library (not plugable for the moment)
 * @param jquery 
 * @param underscore
 */
(function($,_){
    
    var methods = {
        MAX_NB_LEVELS: 5, // constant
        columnview: null,
        options: null,
        get_num: function(node) {
            return parseInt(node.data('num'), 10);//make sure this is an integer
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
        
        // get first element of associative array data
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
        // expand from where we are
        expand_columns: function(path, position) {
            
            var curr_pos   = position;
            
            // get the column view that needs to be populated
            var columnview      = methods.columnview;
            
            var data_to_display = methods.get_data_to_display(path);
            
            while (curr_pos != methods.options.nb_cols)
            {
               var div = methods.create_column(path);
               columnview.append(div);
               methods.set_on_change_listener(div);
               
               // update the path
               data_to_display = methods.get_data_to_display(path);
               
               // while we have more object add them in the path otherwise
               // do nothing and add an empty column for each missing level
               // (use the fact that there are no more path elements and that the path
               // stays constant)
               if (! $.isEmptyObject(data_to_display))
               {
                 path.push(methods.get_first_element(data_to_display));
               }
               
               curr_pos += 1;
               
            }
        },
        // create as many columns as you which (5 should be the maximum)
        create_nlevel_columns: function(orig_path, nb_levels) {
            // get the column view that needs to be populated
            var columnview      = methods.columnview;
    
            var path = _.clone(orig_path); // the path that is constructed dynamically
            
            var data_to_display = methods.get_data_to_display(orig_path);
            
            var i=0;
           
            for (i=0;i<nb_levels;i++)
            {
               var div = methods.create_column(path);	
               
               // add div in cloumnview
               columnview.append(div);
               methods.set_on_change_listener(div);
               
               // update path and data_to_display
               path.push(methods.get_first_element(data_to_display));
               
               data_to_display = methods.get_data_to_display(path);
            }
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
        // create an empty column
        create_empty_column: function() {
            var columnview      = methods.columnview;
       
            var num = methods.inc_num(columnview); //next leaf in columns
            
            div = $('<span class="column"><select class="selector" multiple="multiple"></select></span>');
            
            // always apply the same width for all columns
            div.css('width', methods.options["col_width_"+num]);
            
            div.data('num', num);
            
            columnview.data('num', num);
            
            return div;
        },      
        // create an individual column from a path
        create_column: function(path) {
            var columnview      = methods.columnview;
            
            var data_to_display = methods.get_data_to_display(path);
            
            // if there is some data to display
            var div = null;
            if (_.size(data_to_display) > 0)
            {
                var num = methods.inc_num(columnview); //next leaf in columns
                
                div = $('<span class="column"><select class="selector" multiple="multiple"></select></span>');
                
                // always apply the same width for all columns
                div.css('width', methods.options["col_width_" + num]);
                
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
                      div.find('select').append('<option title="SELECTED" path="'+ methods.path_to_string(n_path) + '" selected="">'+key+'</option>'); 
                   }
                   else
                   {
                      div.find('select').append('<option title="UN SELECTED" path="'+ methods.path_to_string(n_path) + '" >'+key+'</option>');
                   }
                   cpt = cpt + 1;
                });
            }
            else
            {
                div = methods.create_empty_column();
            }

            return div;
        },
        // install listener on change events
        set_on_change_listener: function(column) {

            // use change event to detect keyboard movement and mouse click
            // This will allow to navigate with the mouse or the keyboard 
            // (before it was a click event on options)
            column.find('select').change(function () {
                 var key       = "";
                 var path_attr = "";
                 
                 $(this).find("option:selected").each(function () {
                       key += $(this).text();
                       path_attr = $(this).attr("path");
                 });
                 
                 var position = methods.get_num(column); // get the column position
                 
                 var path = methods.string_to_path(path_attr); // get the path from the element
                  
                 methods.clean_columns(position); // clean from the position
                 
                 methods.expand_columns(path, position); // expand from the position   
            });
        },
        init: function(data, options) {
            
            // check options
            if (_.isNull(options) || _.isUndefined(options))
            {
                // add defaults 
                options = { 'nb_cols' : 3, 'col_width_1' : 200, 'col_width_2' : 200, 'col_width_3' : 200 };
            }
           
            if (_.isUndefined(options.nb_cols))
            {
                options.nb_cols = 3;
            }
            
            _.each(_.range(1, options.nb_cols+1), function(incr) {
                
                if (_.isUndefined(options["col_width_" + incr]))
                {
                    options["col_width_" + incr] = 200;
                }
                
            });
            
            methods.options = options;
            var columnview  = methods.columnview;
            
            columnview.data('num', 0); //init column counter
            columnview.data('data', data);//add the data in the dom
            columnview.data('path', []);// list of keys where we are in the data
            
            methods.create_nlevel_columns(columnview.data('path'), methods.options.nb_cols); // instanciate column view structure          
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