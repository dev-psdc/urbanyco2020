/* This inherits actions and screens have been removed on the new version 3.0.0 the logic has been changed. */
odoo.define('fpi_pos.fiscalprinter', function (require) {
  "use strict";
  var models = require('point_of_sale.models');
  var _super_model = models.PosModel.prototype;
  var screens = require('point_of_sale.screens');
  var gui = require('point_of_sale.gui');
  var core = require('web.core');
  var _t = core._t;
  var _order_model = models.Order.prototype;
  models.Order = models.Order.extend({
    initialize: function (attributes, options) {
      _order_model.initialize.call(this, attributes, options);
      this.fiscal_printer_allowed = this.fiscal_printer_allowed || false;
    },
    export_as_JSON: function () {
      var data = _order_model.export_as_JSON.call(this);
      var fiscal_printer_allowed = false;
      if ( 'fiscal_printer_allowed' in this ) {
        if ( this.fiscal_printer_allowed ) {
          fiscal_printer_allowed = true;
        }
      }
      data.fiscal_printer_allowed = fiscal_printer_allowed;
      return data;
    }
  });
  models.PosModel = models.PosModel.extend({
    initialize: function (session, attributes) {
      self.fpi_printers = [];
      console.log("Installing the FPI POS module.");
      var printer_model = {
        model: 'fpi.printer',
        fields: ['id', 'employee_id', 'is_available', 'model', 'serial'],
        loaded: function(self, fpi_printers) {
          self.fpi_printers = fpi_printers;
        }
      };
      this.models.push(printer_model);
      return _super_model.initialize.call(this, session, attributes);
    },
    push_and_invoice_order: function(order) {
      var self = this;
      var invoiced = new $.Deferred(); 
      if(!order.get_client()){
        invoiced.reject({code:400, message:'Missing Customer', data:{}});
        return invoiced;
      }
      var order_id = this.db.add_order(order.export_as_JSON());
      this.flush_mutex.exec(function(){
        var done = new $.Deferred(); // holds the mutex
        var transfer = self._flush_orders([self.db.get_order(order_id)], {timeout:30000, to_invoice:true});
        transfer.fail(function(error){
          invoiced.reject(error);
          done.reject();
        });
        transfer.pipe(function(order_server_id) {
          /* Fix applied, the code that allow to generate automatically the PDF when an order is invoiced have been removed. */
          invoiced.resolve();
          done.resolve();
        });
        return done;
      });
      return invoiced;
    }
  });
  var NeonetyPaymentScreenWidget = screens.PaymentScreenWidget.extend({
    init: function(parent, options) {
      var self = this;
      this._super(parent, options);
    },
    finalize_validation: function () {
      var self = this;
      var screen = this;
      if (this.pos.config.iface_fiscal_printer_optional) {
        self.gui.show_popup('confirm',{
          'title': 'Confirmación',
          'body': '¿Desea enviar la orden a la impresora fiscal?.',
          confirm: function(){
            screen.fpi_print_invoice_action(true);
          },
          cancel: function () {
            screen.fpi_print_invoice_action(false);
          }
        });
      } else {
        if ( this.pos.config.iface_fiscal_printer_button ) {
          this.fpi_print_invoice_action(true);
        } else {
          this.fpi_print_invoice_action(false);
        }
      }
    },
    fpi_print_invoice_action: function (flag) {
      var self = this;
      var order = this.pos.get_order();
      if (order.is_paid_with_cash() && this.pos.config.iface_cashdrawer) { 
        this.pos.proxy.open_cashbox();
      }
      order.fiscal_printer_allowed = flag;
      if (!flag) {
        order.initialize_validation_date();
        order.finalized = true;
        if (order.is_to_invoice()) {
          var invoiced = this.pos.push_and_invoice_order(order);
          this.invoicing = true;
          invoiced.fail(function(error){
            self.invoicing = false;
            order.finalized = false;
            if (error.message === 'Missing Customer') {
              self.gui.show_popup('confirm',{
                'title': _t('Please select the Customer'),
                'body': _t('You need to select the customer before you can invoice an order.'),
                confirm: function(){
                  self.gui.show_screen('clientlist');
                },
              });
            } else if (error.code < 0) {        // XmlHttpRequest Errors
              self.gui.show_popup('error',{
                'title': _t('The order could not be sent'),
                'body': _t('Check your internet connection and try again.'),
              });
            } else if (error.code === 200) {    // OpenERP Server Errors
              self.gui.show_popup('error-traceback',{
                'title': error.data.message || _t("Server Error"),
                'body': error.data.debug || _t('The server encountered an error while receiving your order.'),
              });
            } else {                            // ???
              self.gui.show_popup('error',{
                'title': _t("Unknown Error"),
                'body':  _t("The order could not be sent to the server due to an unknown error"),
              });
            }
          });
          invoiced.done(function(){
            self.invoicing = false;
            self.gui.show_screen('receipt');
          });
        } else {
          this.pos.push_order(order);
          this.gui.show_screen('receipt');
        }
      } else {
        var cashier = this.pos.attributes.cashier;
        var can_fiscal_print = false;
        for ( var i = 0; i < self.pos.fpi_printers.length; i++ ) {
          if ( cashier.id == self.pos.fpi_printers[i].employee_id[0] ) {
            can_fiscal_print = true;
            break;
          }
        }
        if ( ! can_fiscal_print ) {
          self.gui.show_popup('error',{
            'title': _t('La orden no se puede imprimir en la impresora fiscal'),
            'body': _t('No se ha podido imprimir el documento ya que el usuario no tiene una impresora fiscal asignada.'),
          });
        } else {
          order.initialize_validation_date();
          if (order.is_to_invoice()) {  
            var invoiced = this.pos.push_and_invoice_order(order);
            this.invoicing = true;
            invoiced.fail(function(error){
              self.invoicing = false;
              if (error.message === 'Missing Customer') {
                self.gui.show_popup('confirm',{
                  'title': _t('Please select the Customer'),
                  'body': _t('You need to select the customer before you can invoice an order.'),
                  confirm: function(){
                    self.gui.show_screen('clientlist');
                  },
                });
              } else if (error.code < 0) {        // XmlHttpRequest Errors
                self.gui.show_popup('error',{
                  'title': _t('The order could not be sent'),
                  'body': _t('Check your internet connection and try again.'),
                });
              } else if (error.code === 200) {    // OpenERP Server Errors
                self.gui.show_popup('error-traceback',{
                  'title': error.data.message || _t("Server Error"),
                  'body': error.data.debug || _t('The server encountered an error while receiving your order.'),
                });
              } else {                            // ???
                self.gui.show_popup('error',{
                  'title': _t("Unknown Error"),
                  'body':  _t("The order could not be sent to the server due to an unknown error"),
                });
              }
            });
            invoiced.done(function(){
              self.invoicing = false;
              self.gui.show_screen('receipt');
            });
          } else {
            if ( !order.get_client() ) {
              self.gui.show_popup('error',{
                'title': _t('Please select the Customer'),
                'body': _t('You need to select the customer before you can invoice an order.')
              });
            } else {
              this.pos.push_order(order);
              this.gui.show_screen('receipt');
            }
          }
        }
      }
    }
  });
  gui.define_screen({name:'payment', widget: NeonetyPaymentScreenWidget});
});