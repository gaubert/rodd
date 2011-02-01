/**
 * First version of the rodd library (not plugable for the moment)
 * @param jquery 
 * @param underscore
 */
(function($,_){
    
    var RCV = {
        
        columnview: null,
        
        hello:function(){
            alert("In HELLO");
        },
        
        get_num: function(node) {
            return parseInt(node.data('num'));//make sure this is an integer
        },
        inc_num: function(node) {
            node.data('num', this.get_num(node)+1);
            return this.get_num(node);
        },
        dec_num: function(node) {
            node.data('num', this.get_num(node)-1);
            return this.get_num(node);
        },
        
        create_column: function(node) {
            var num = this.inc_num(node); //next leaf in columns
            var div = $('<div class="column" style="float:left;"></div>');
            //if(methods.options && methods.options.columns)
            //   div.css('width', methods.options.columns[num]); //apply a width if we have one
            div.data('num', num);
            this.columnview.data('num', num);
            return div;
        },
        
        
        load:function(elem_name) {
            
            // get local dom element called elem_name
            var dom_elem = $(elem_name);
            
            this.columnview = dom_elem;
            
            jQuery.data(dom_elem,"num",0);
            
            //alert("num:" + jQuery.data(dom_elem, "num"));
            
            div = this.create_column(dom_elem);
            div.html(this.columnview.contents().detach()).appendTo(this.columnview); //replace contents into new column
            //methods.setup_links(div);
        }
    
    }; 
    
     if(!window.rcv){window.rcv=RCV;};
  
    
})(jQuery,_);