odoo.define('rdv_row_per_view', function (require) {
"use strict";
    
var core = require('web.core');
var data = require('web.data');
var ListView = require('web.ListView');
var Model = require('web.DataModel');
var form_widget = require('web.form_widgets');
var _t = core._t;

var QWeb = core.qweb;

form_widget.WidgetButton.include({
    on_click: function() {
        var self=this;
         if(this.node.attrs.custom === "click"){
            var rows=$('.temp_row').val();
            new Model('rdv.record').call('write', [[this.view.datarecord.id], {'rows': rows}]).then(function (incomming_id) {
                window.location.reload();
            });
            return;
         }
         this._super();
    },
});


ListView.include({
    init: function() {
        var self = this;
        this._super.apply(this, arguments);
        
    },
    start:function(){
        var self = this;
        this._super.apply(this, arguments);
        if(self.dataset){
            if(self.dataset.parent_view){
                if(self.dataset.parent_view.datarecord){
                    if(self.dataset.parent_view.datarecord.rows){
                        this._limit=self.dataset.parent_view.datarecord.rows
                    }
                }
            }
        
        }
        // console.log(self.dataset.parent_view.datarecord.rows)
    },

});
});
