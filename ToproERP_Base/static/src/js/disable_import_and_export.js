odoo.define('ToproERP_Base.disable_import_and_export', function (require) {
    "use strict";

    var core = require('web.core');
    var ListView = require('web.ListView');
    var session = require('web.session');
    var Model = require('web.DataModel');

    var _t = core._t;

    ListView.include({
    /**
     * Extend the render_buttons function of ListView by adding an event listener
     * on the import button.
     * @return {jQuery} the rendered buttons
     */
        render_buttons: function() {   //只有管理员可以导入
            var self = this;

            this._super.apply(this, arguments); // Sets this.$buttons
            if (session.uid != 1)
                self.$buttons.find('.o_list_button_import').hide();

            return this.$buttons;
        },

        render_sidebar: function() {  //只有管理员可以导出
            var self = this;

            this._super.apply(this, arguments);
            return new Model("res.users")
                .query(["allow_export"])
                .filter([["id", "=", session.uid]])
                .first()
                .done(function(result) {
                   if (!result['allow_export'] && self.sidebar){
                    self.sidebar.$('li:contains("'+_t("Export")+'")').remove();
                   }

                   return self.sidebar;
                });

        },
    });


});