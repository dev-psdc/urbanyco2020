odoo.define('neonety_pos.neonetyscreen', function (require) {
  "use strict";
  var screens = require('point_of_sale.screens');
  var chrome = require('point_of_sale.chrome');
  var gui = require('point_of_sale.gui');
  var DomCache = screens.DomCache;
  var models = require('point_of_sale.models');
  var core = require('web.core');
  var rpc = require('web.rpc');
  var utils = require('web.utils');
  var QWeb = core.qweb;
  var _t = core._t;
  var round_pr = utils.round_precision;
  console.log("Installing the Nonety POS screen widget plugin.");
  var NeonetyUsernameWidget = chrome.UsernameWidget.include({
    disable_buttons: function (user) {
      var disable_button = user.role == 'manager' ? false : true;
      var buttons = document.getElementsByClassName('mode-button');
      if ( buttons.length > 0 ) {
        for( var i = 0; i < buttons.length; i++ ) {
          var data_mode = buttons[i].getAttribute('data-mode');
          if ( data_mode && data_mode != 'quantity' ) {
            buttons[i].disabled = disable_button;
          }
        }
      }
      var backspace_buttons = document.getElementsByClassName('neonety-numpad-backspace');
      if ( backspace_buttons.length > 0 ) {
        var backspace_button = backspace_buttons[0];
        backspace_button.disabled = disable_button;
      }
    },
    renderElement: function () {
      this._super();
    },
    get_name: function(){
      var user = this.pos.attributes.cashier || this.pos.user;
      if(user){
        this.disable_buttons(user);
        return user.name;
      }else{
        return "";
      }
    },
  });
  var NeonetyClientListScreenWidget = screens.ScreenWidget.extend({
    template: 'ClientListScreenWidget',
    init: function(parent, options) {
      this._super(parent, options);
      this.partner_cache = new DomCache();
      if ( this.pos.attributes ) {
        var disable_button = this.pos.attributes.cashier.role == 'manager' ? false : true;
        var buttons = document.getElementsByClassName('mode-button');
        if ( buttons.length > 0 ) {
          for( var i = 0; i < buttons.length; i++ ) {
            var data_mode = buttons[i].getAttribute('data-mode');
            if ( data_mode && data_mode != 'quantity' ) {
              buttons[i].disabled = disable_button;
            }
          }
        }
        var backspace_buttons = document.getElementsByClassName('neonety-numpad-backspace');
        if ( backspace_buttons.length > 0 ) {
          var backspace_button = backspace_buttons[0];
          backspace_button.disabled = disable_button;
        }
      }
    },
    auto_back: true,
    show: function(){
      var self = this;
      this._super();
      this.renderElement();
      this.details_visible = false;
      this.old_client = this.pos.get_order().get_client();
      this.$('.back').click(function(){
        self.gui.back();
      });
      this.$('.next').click(function(){   
        self.save_changes();
        self.gui.back();    // FIXME HUH ?
      });
      this.$('.new-customer').click(function(){
        self.display_client_details('edit',{
          'country_id': self.pos.company.country_id,
        });
      });
      var partners = this.pos.db.get_partners_sorted(1000);
      this.render_list(partners);
      this.reload_partners();
      if( this.old_client ){
        this.display_client_details('show',this.old_client,0);
      }
      this.$('.client-list-contents').delegate('.client-line','click',function(event){
        self.line_select(event,$(this),parseInt($(this).data('id')));
      });
      var search_timeout = null;
      if(this.pos.config.iface_vkeyboard && this.chrome.widget.keyboard){
        this.chrome.widget.keyboard.connect(this.$('.searchbox input'));
      }
      this.$('.searchbox input').on('keypress',function(event){
        clearTimeout(search_timeout);
        var query = this.value;
        search_timeout = setTimeout(function(){
          self.perform_search(query,event.which === 13);
        },70);
      });
      this.$('.searchbox .search-clear').click(function(){
        self.clear_search();
      });
    },
    hide: function () {
      this._super();
      this.new_client = null;
    },
    barcode_client_action: function(code){
      if (this.editing_client) {
        this.$('.detail.barcode').val(code.code);
      } else if (this.pos.db.get_partner_by_barcode(code.code)) {
        var partner = this.pos.db.get_partner_by_barcode(code.code);
        this.new_client = partner;
        this.display_client_details('show', partner);
      }
    },
    perform_search: function(query, associate_result){
      var customers;
      if(query){
        customers = this.pos.db.search_partner(query);
        this.display_client_details('hide');
        if ( associate_result && customers.length === 1){
          this.new_client = customers[0];
          this.save_changes();
          this.gui.back();
        }
        this.render_list(customers);
      }else{
        customers = this.pos.db.get_partners_sorted();
        this.render_list(customers);
      }
    },
    clear_search: function(){
      var customers = this.pos.db.get_partners_sorted(1000);
      this.render_list(customers);
      this.$('.searchbox input')[0].value = '';
      this.$('.searchbox input').focus();
    },
    render_list: function(partners){
      var contents = this.$el[0].querySelector('.client-list-contents');
      contents.innerHTML = "";
      for(var i = 0, len = Math.min(partners.length,1000); i < len; i++){
        var partner    = partners[i];
        var clientline = this.partner_cache.get_node(partner.id);
        if(!clientline){
          var clientline_html = QWeb.render('ClientLine',{widget: this, partner:partners[i]});
          var clientline = document.createElement('tbody');
          clientline.innerHTML = clientline_html;
          clientline = clientline.childNodes[1];
          this.partner_cache.cache_node(partner.id,clientline);
        }
        if( partner === this.old_client ){
          clientline.classList.add('highlight');
        }else{
          clientline.classList.remove('highlight');
        }
        contents.appendChild(clientline);
      }
    },
    save_changes: function(){
      var self = this;
      var order = this.pos.get_order();
      if( this.has_client_changed() ){
        if ( this.new_client ) {
          order.fiscal_position = _.find(this.pos.fiscal_positions, function (fp) {
            return fp.id === self.new_client.property_account_position_id[0];
          });
        } else {
          order.fiscal_position = undefined;
        }
        order.set_client(this.new_client);
      }
    },
    has_client_changed: function(){
      if( this.old_client && this.new_client ){
        return this.old_client.id !== this.new_client.id;
      }else{
        return !!this.old_client !== !!this.new_client;
      }
    },
    toggle_save_button: function(){
      var $button = this.$('.button.next');
      if (this.editing_client) {
        $button.addClass('oe_hidden');
        return;
      } else if( this.new_client ){
        if( !this.old_client){
          $button.text(_t('Set Customer'));
        }else{
          $button.text(_t('Change Customer'));
        }
      }else{
        $button.text(_t('Deselect Customer'));
      }
      $button.toggleClass('oe_hidden',!this.has_client_changed());
    },
    line_select: function(event,$line,id){
      var partner = this.pos.db.get_partner_by_id(id);
      this.$('.client-list .lowlight').removeClass('lowlight');
      if ( $line.hasClass('highlight') ){
        $line.removeClass('highlight');
        $line.addClass('lowlight');
        this.display_client_details('hide',partner);
        this.new_client = null;
        this.toggle_save_button();
      }else{
        this.$('.client-list .highlight').removeClass('highlight');
        $line.addClass('highlight');
        var y = event.pageY - $line.parent().offset().top;
        this.display_client_details('show',partner,y);
        this.new_client = partner;
        this.toggle_save_button();
      }
    },
    partner_icon_url: function(id){
      return '/web/image?model=res.partner&id='+id+'&field=image_small';
    },
    edit_client_details: function(partner) {
      if ( partner.province_id && partner.province_id.length > 0 ) {
        this.apply_districts_filter(partner, partner.province_id[0]);  
      }
      if ( partner.district_id && partner.district_id.length > 0 ) {
        this.apply_sectors_filter(partner, partner.district_id[0]);  
      }
      this.display_client_details('edit',partner);
    },
    undo_client_details: function(partner) {
      if (!partner.id) {
        this.display_client_details('hide');
      } else {
        this.display_client_details('show',partner);
      }
    },
    save_client_details: function(partner) {
      var self = this;
      var fields = {};
      this.$('.client-details-contents .detail').each(function(idx,el){
        fields[el.name] = el.value || false;
      });
      if (!fields.name) {
        this.gui.show_popup('error',_t('A Customer Name Is Required'));
        return;
      }
      if (!fields.ruc) {
        this.gui.show_popup('error',_t('El campo RUC es requerido'));
        return;
      }
      if (!fields.province_id) {
        this.gui.show_popup('error',_t('El campo Provincia es requerido'));
        return;
      }
      if (!fields.district_id) {
        this.gui.show_popup('error',_t('El campo Distrito es requerido'));
        return;
      }
      if (!fields.sector_id) {
        this.gui.show_popup('error',_t('El campo Corregimiento es requerido'));
        return;
      }
      if (!fields.street) {
        this.gui.show_popup('error',_t('El campo Lugar es requerido'));
        return;
      }
      if (this.uploaded_picture) {
        fields.image = this.uploaded_picture;
      }
      fields.id = partner.id || false;
      fields.country_id = fields.country_id || false;
      rpc.query({
        model: 'res.partner',
        method: 'create_from_ui',
        args: [fields],
      })
      .then(function(partner_id){
        self.saved_client_details(partner_id);
      },function(type,err){
        var error_body = _t('Your Internet connection is probably down.');
        if (err.data) {
          var except = err.data;
          error_body = except.arguments && except.arguments[0] || except.message || error_body;
        }
        self.gui.show_popup('error',{
          'title': _t('Error: Could not Save Changes'),
          'body': error_body,
        });
      });
    },
    saved_client_details: function(partner_id){
      var self = this;
      this.reload_partners().then(function(){
        var partner = self.pos.db.get_partner_by_id(partner_id);
        if (partner) {
          self.new_client = partner;
          self.toggle_save_button();
          self.display_client_details('show',partner);
        } else {
          self.display_client_details('hide');
        }
      });
    },
    resize_image_to_dataurl: function(img, maxwidth, maxheight, callback){
      img.onload = function(){
        var canvas = document.createElement('canvas');
        var ctx    = canvas.getContext('2d');
        var ratio  = 1;
        if (img.width > maxwidth) {
          ratio = maxwidth / img.width;
        }
        if (img.height * ratio > maxheight) {
          ratio = maxheight / img.height;
        }
        var width  = Math.floor(img.width * ratio);
        var height = Math.floor(img.height * ratio);
        canvas.width  = width;
        canvas.height = height;
        ctx.drawImage(img,0,0,width,height);
        var dataurl = canvas.toDataURL();
        callback(dataurl);
      };
    },
    load_image_file: function(file, callback){
      var self = this;
      if (!file.type.match(/image.*/)) {
        this.gui.show_popup('error',{
          title: _t('Unsupported File Format'),
          body:  _t('Only web-compatible Image formats such as .png or .jpeg are supported'),
        });
        return;
      }
      var reader = new FileReader();
      reader.onload = function(event){
        var dataurl = event.target.result;
        var img     = new Image();
        img.src = dataurl;
        self.resize_image_to_dataurl(img,800,600,callback);
      };
      reader.onerror = function(){
        self.gui.show_popup('error',{
          title :_t('Could Not Read Image'),
          body  :_t('The provided file could not be read due to an unknown error'),
        });
      };
      reader.readAsDataURL(file);
    },
    reload_partners: function(){
      var self = this;
      return this.pos.load_new_partners().then(function(){
        self.render_list(self.pos.db.get_partners_sorted(1000));
        var curr_client = self.pos.get_order().get_client();
        if (curr_client) {
          self.pos.get_order().set_client(self.pos.db.get_partner_by_id(curr_client.id));
        }
      });
    },
    apply_districts_filter: function (partner, province_id) {
      var self = this;
      var tmp_districts = [];
      for( var i = 0; i < self.pos.districts.length; i++ ) {
        if ( self.pos.districts[i].province_id[0] == province_id ) {
          tmp_districts.push(self.pos.districts[i])
        }
      }
      self.pos.districts_filtered = tmp_districts;
      var dynamic_options = '<option value=""></option>';
      for( var i = 0; i < self.pos.districts_filtered.length; i++ ) {
        dynamic_options += '<option value="' + self.pos.districts_filtered[i].id + '">' + self.pos.districts_filtered[i].name + '</option>';
      }
      self.$('select.client-address-district').find('option').remove().end().append(dynamic_options);
      self.$('select.client-address-sector').find('option').remove().end();
    },
    apply_sectors_filter: function (partner, district_id) {
      var self = this;
      var tmp_sectors = [];
      for( var i = 0; i < self.pos.sectors.length; i++ ) {
        if ( self.pos.sectors[i].district_id[0] == district_id ) {
          tmp_sectors.push(self.pos.sectors[i])
        }
      }
      self.pos.sectors_filtered = tmp_sectors;
      var dynamic_options = '<option value=""></option>';
      for( var i = 0; i < self.pos.sectors_filtered.length; i++ ) {
        dynamic_options += '<option value="' + self.pos.sectors_filtered[i].id + '">' + self.pos.sectors_filtered[i].name + '</option>';
      }
      self.$('select.client-address-sector').find('option').remove().end().append(dynamic_options);
    },
    display_client_details: function(visibility,partner,clickpos){
      var self = this;
      var contents = this.$('.client-details-contents');
      var parent   = this.$('.client-list').parent();
      var scroll   = parent.scrollTop();
      var height   = contents.height();
      contents.off('click','.button.edit'); 
      contents.off('click','.button.save'); 
      contents.off('click','.button.undo'); 
      contents.on('click','.button.edit',function(){ self.edit_client_details(partner); });
      contents.on('click','.button.save',function(){ self.save_client_details(partner); });
      contents.on('click','.button.undo',function(){ self.undo_client_details(partner); });
      contents.on('change', '.client-address-province', function () {
        var province_id = self.$('.client-address-province option:selected').val();
        self.apply_districts_filter(partner, province_id);
      });
      contents.on('change', '.client-address-district', function () {
        var district_id = self.$('.client-address-district option:selected').val();
        self.apply_sectors_filter(partner, district_id);
      });
      contents.on('change', '.client-birth-date', function() {
        var birthDateStr = self.$('input.client-birth-date').val();
        if ( birthDateStr != null && birthDateStr != undefined ) {
          var birthDateSplited = birthDateStr.split('-');
          if ( birthDateSplited.length == 3 ) {
            var birthDate = new Date(birthDateSplited[0], birthDateSplited[1] - 1, birthDateSplited[2]);
            var diffMs = Date.now() - birthDate.getTime();
            var ageDT = new Date(diffMs);
            var age = Math.abs(ageDT.getUTCFullYear() - 1970);
            if ( age > 0) {
              self.$('input.client-age').val(age + ' año(s) de edad.');
            }
          }
        }
      });
      this.editing_client = false;
      this.uploaded_picture = null;
      if(visibility === 'show'){
        contents.empty();
        contents.append($(QWeb.render('ClientDetails',{widget:this,partner:partner})));
        var new_height   = contents.height();
        if(!this.details_visible){
          parent.height('-=' + new_height);
          if(clickpos < scroll + new_height + 20 ){
            parent.scrollTop( clickpos - 20 );
          }else{
            parent.scrollTop(parent.scrollTop() + new_height);
          }
        }else{
          parent.scrollTop(parent.scrollTop() - height + new_height);
        }
        this.details_visible = true;
        this.toggle_save_button();
      } else if (visibility === 'edit') {
        this.editing_client = true;
        contents.empty();
        contents.append($(QWeb.render('ClientDetailsEdit',{widget:this,partner:partner})));
        this.toggle_save_button();
        contents.find('input').blur(function() {
          setTimeout(function() {
            self.$('.window').scrollTop(0);
          }, 0);
        });
        contents.find('.image-uploader').on('change',function(event){
          self.load_image_file(event.target.files[0],function(res){
            if (res) {
              contents.find('.client-picture img, .client-picture .fa').remove();
              contents.find('.client-picture').append("<img src='"+res+"'>");
              contents.find('.detail.picture').remove();
              self.uploaded_picture = res;
            }
          });
        });
      } else if (visibility === 'hide') {
        contents.empty();
        parent.height('100%');
        if( height > scroll ){
          contents.css({height:height+'px'});
          contents.animate({height:0},400,function(){
            contents.css({height:''});
          });
        }else{
          parent.scrollTop( parent.scrollTop() - height);
        }
        this.details_visible = false;
        this.toggle_save_button();
      }
    },
    close: function(){
      this._super();
    },
  });
  gui.define_screen({name:'clientlist', widget: NeonetyClientListScreenWidget});
});