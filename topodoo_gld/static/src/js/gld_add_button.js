openerp.syt_oa = function(instance) {
	var MODELS_NOT_TO_HIDE = ['gld'];
	// instance.web.FormView.prototype.defaults.save_and_sent = true;
	instance.web.FormView.include({
		load_form : function(data) {
			var self = this;
			var add_button = false;
			var res_model = self.dataset.model;
			if (!self.$buttons) {
				add_button = true;
			}
			var ret = self._super.apply(self, arguments);
			if ($.inArray(res_model, MODELS_NOT_TO_HIDE) == -1) {
				self.$buttons.find('.oe_form_button_save_sent_gld').remove();
				//隐藏按钮
			}
			if (add_button) {
				self.$buttons.on('click', '.oe_form_button_save_sent_gld', function() {
					$.when(self.save()).done(function() {
						// 提交工联单
						var ids = self.get_selected_ids();
						self.rpc("/gld/sent",{gld_id:ids}).done(function() {
							self.reload().then(function() {
								self.to_view_mode();
							});
						});
					});
					self.do_action({
						//pop window
					});
				});
			}
			return ret;
		},
	});
};
