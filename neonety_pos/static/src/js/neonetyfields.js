odoo.define('neonety_pos.neonetyfields', function (require) {
  "use strict";
  var core = require('web.core');
  var _t = core._t;
  var models = require('point_of_sale.models');
  var _super_model = models.PosModel.prototype;
  models.PosModel = models.PosModel.extend({
    initialize: function (session, attributes) {
      console.log("Neonety POS module installed.");
      self.districts_filtered = [];
      self.sectors_filtered = [];
      var partner_model = _.find(this.models, function (model) {
        return model.model == 'res.partner';
      });
      var province_model = {
        model: 'neonety.province',
        fields: ['id', 'code', 'name', 'country_id'],
        loaded: function(self, provinces) {
          self.provinces = provinces;
        }
      };
      var district_model = {
        model: 'neonety.district',
        fields: ['id', 'code', 'name', 'province_id', 'country_id'],
        loaded: function(self, districts) {
          self.districts = districts;
          self.districts_filtered = self.districts;
        }
      };
      var sector_model = {
        model: 'neonety.sector',
        fields: ['id', 'code', 'name', 'district_id', 'province_id', 'country_id'],
        loaded: function(self, sectors) {
          self.sectors = sectors;
          self.sectors_filtered = sectors;
        }
      };
      this.models.push(province_model, district_model, sector_model);
      partner_model.fields.push('ruc', 'dv', 'neonety_country_id', 'province_id', 'district_id', 'sector_id', 'sex', 'birth_date', 'age');
      return _super_model.initialize.call(this, session, attributes);
    },
  });
  var _order_model = models.Order.prototype;
  models.Order = models.Order.extend({
    initialize: function (attributes,options) {
      _order_model.initialize.call(this, attributes, options);
      var self = this;
      options  = options || {};
      this.pos = options.pos;
      if ( this.pos.config.iface_allow_default_partner ) {
        if ( 'attributes' in this ) {
          if ( 'client' in this.attributes ) {
            var default_partner_id = 0;
            var default_partner = null;
            if ( 'iface_default_partner_id' in this.pos.config ) {
              default_partner_id = this.pos.config.iface_default_partner_id[0];
            }
            for ( var i = 0; i < this.pos.partners.length; i++ ) {
              if ( ! default_partner && this.pos.partners[i].id == default_partner_id ) {
                default_partner = this.pos.partners[i];
                break;
              }
            }
            if ( default_partner ) {
              this.attributes.client = default_partner;
            }
          }
        }
      }
      this.save_to_db();
    },
    add_product: function(product, options){
      if(this._printed){
        this.destroy();
        return this.pos.get_order().add_product(product, options);
      }
      this.assert_editable();
      options = options || {};
      var attr = JSON.parse(JSON.stringify(product));
      attr.pos = this.pos;
      attr.order = this;
      var line = new models.Orderline({}, {pos: this.pos, order: this, product: product});
      if(options.quantity !== undefined){
        line.set_quantity(options.quantity);
      }
      if(options.price !== undefined){
        line.set_unit_price(options.price);
      }
      this.fix_tax_included_price(line);
      if(options.discount !== undefined){
        line.set_discount(options.discount);
      }
      if(options.extras !== undefined){
        for (var prop in options.extras) {
          line[prop] = options.extras[prop];
        }
      }
      var last_orderline = this.get_last_orderline();
      if ( this.pos.config.iface_no_merge_products ) {
        this.orderlines.add(line);
      } else {
        if( last_orderline && last_orderline.can_be_merged_with(line) && options.merge !== false){
          last_orderline.merge(line);
        }else{
          this.orderlines.add(line);
        }
      }
      this.select_orderline(this.get_last_orderline());
      if(line.has_product_lot){
        this.display_lot_popup();
      }
    }
  });
});