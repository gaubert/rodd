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
        get_data_to_display:function(key_list) {
            var columnview = methods.columnview;
            var data_to_display = columnview.data('data');
            
            var val = data_to_display;
        
            if  (key_list.length > 0)
            {
              _.each(key_list, function(key) { val = val[key] }); //iterate over each key to go to the right values
            }
         
            return val;
        },
        reduce_key_list:function(n) {
            var columnview = methods.columnview;
            
            var key_list   = columnview.data('key_list');
            
            key_list = _.first(key_list,n);
            
            columnview.data('key_list',key_list); //update key_list
            
            return key_list;
        },
        expand: function(key_list, col) {
            var columnview = methods.columnview;
            var seek = null;
            
            //Clean the different columns
            columnview.find('.column').each(function() {
                var colnum = methods.get_num($(this));
                if(colnum == col) 
                {
                    seek = $(this);
                    seek.empty();
                    methods.reduce_key_list(col);
                } 
                else if(colnum > col) 
                {
                    $(this).remove(); //kill leaves that no longer apply to new child
                    methods.dec_num(columnview);
                    key_list = methods.reduce_key_list(col);
                }
            });
            if(!seek) {
                seek = methods.create_column(key_list);
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
        create_column: function(key_list) {
            var columnview      = methods.columnview;
            var data_to_display = methods.get_data_to_display(key_list);
            // if there is some data to display
            var div = null;
            if (_.size(data_to_display) > 0)
            {
                var num = methods.inc_num(columnview); //next leaf in columns
                
                div = $('<div class="column" style="float:left;"><ul></ul></div>');
                
                if(methods.options && methods.options.columns)
                {
                    div.css('width', methods.options.columns[num]); //apply a width if we have one
                }
                 
                div.data('num', num);
                columnview.data('num', num);
                
                console.log("data_to_display" + data_to_display);
                
                // for each data line add a <li> tag
                
                _.each(data_to_display, function(val, key) { 
                                    div.find('ul').append('<li><a href="search.html">' + key + '</a></li>'); 
                });
            }

            return div;
        },
        setup_links: function(column) {
            column.find('a:not(.ignore-link)').each(function() {
                $(this).click(function(evt) {
                    
                    var key = $(this).text();
                    key_list = methods.columnview.data('key_list');
                    key_list.push(key);
                    
                    column.find('a.selected').removeClass('selected').trigger('columnview-deselected');
                    var num = methods.get_num(column);
                    var url = $(this).attr('href');
                    methods.expand(key_list, num+1); //expand into the next column
                    $(this).addClass('selected').trigger('columnview-selected');
                    evt.preventDefault();
                    return false;
                });
            });
        },
        init: function(data, options) {
            methods.options = options;
            console.log(data);
            var columnview = methods.columnview;
            columnview.data('num', 0); //init column counter
            columnview.data('data', data);//add the data in the dom
            columnview.data('key_list', []);// list of keys where we are in the data
            div = methods.create_column(columnview.data('key_list'));
            //div.html(columnview.contents().detach()).appendTo(columnview); //replace contents into new column
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