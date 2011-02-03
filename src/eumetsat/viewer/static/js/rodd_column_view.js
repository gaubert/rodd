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
        
            if  (path.length > 0)
            {
              _.each(path, function(key) { val = val[key]; }); //iterate over each key to go to the right values
            }
         
            return val;
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
        /*reduce_key_list:function(value) {
            var columnview = methods.columnview;
            
            var key_list   = columnview.data('key_list');
            
            var index = _.indexOf(key_list, value);
            
            key_list = _.first(key_list, index);
            
            
            columnview.data('key_list',key_list); //update key_list
            
            return key_list;
        },*/
        
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
        create_column: function(path) {
            var columnview      = methods.columnview;
            
            var data_to_display = methods.get_data_to_display(path);
            
            // if there is some data to display
            var div = null;
            if (_.size(data_to_display) > 0)
            {
                var num = methods.inc_num(columnview); //next leaf in columns
                
                //div = $('<span class="column" style="float:left;"><ul class="list"></ul></span>');
                div = $('<span class="column" style="float:left;"><select multiple="multiple"></select></span>');
                
                if(methods.options && methods.options.columns)
                {
                    div.css('width', methods.options.columns[num]); //apply a width if we have one
                }
                 
                div.data('num', num);
                columnview.data('num', num);
               
                // for each data line add a <li> tag
                _.each(data_to_display, function(val, key) { 
                                    //div.find('ul').append('<li><a href="error.html">' + key + '</a></li>');
                            div.find('select').append('<option>'+key+'</option>');
                });
            }

            return div;
        },
        setup_links: function(column) {
            //column.find('a:not(.ignore-link)').each(function() {
            column.find('option').each(function() {
                $(this).click(function(evt) {
                    
                    var key = $(this).text();   // the key clicked on
                    var position = methods.get_num(column); //the current position
                    
                    methods.reduce_path(position);
                    
                    var path = methods.columnview.data('path');
                    
                    // add selected element in path
                    path.push(key);
                    
                    column.find('a.selected').removeClass('selected').trigger('columnview-deselected');
                   
                    var url = $(this).attr('href');
                    methods.expand(path, position+1); //expand into the next column
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
            div = methods.create_column(columnview.data('path'));
            columnview.append(div);
            methods.setup_links(div);
        }
    };
        
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