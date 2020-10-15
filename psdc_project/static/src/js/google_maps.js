odoo.define('psdc_project.google_maps', function (require) {
  "use strict";
  var field_registry = require('web.field_registry');
  var AbstractField = require('web.AbstractField');
  var FormController = require('web.FormController');
  var rpc = require('web.rpc');
  FormController.include({
    _update: function () {
      var _super_update = this._super.apply(this, arguments);
      this.trigger('view_updated');
      return _super_update;
    },
  });
  var MapField = AbstractField.extend({
    template: 'MapField',
    start: function () {
      var self = this;
      this.markers = [];
      this.markerItems = [];
      this.getParent().getParent().on('view_updated', self, function () {
        this.el.classList.remove('o_field_empty');
        self.init_map();
      });
      return this._super();
    },
    init_map: function () {
      var self = this;
      this.map = new google.maps.Map(this.el, {
        center: {lat: 8.9946757, lng: -79.5364582},
        zoom: 14
      });
      rpc.query({
        model: 'psdc_project.task_history',
        method: 'search_read',
        args: [[
          ['task_id', '=', this.res_id]
        ]]
      }).then(function (data) {
        self.setMarkers(data);
      }, function (errors) {
        console.error(errors);
      });
      this.isMap = true;
    },
    setMarkers: function (data) {
      var self = this;
      var GeoPosition = class GeoPosition {
        constructor(latitude, longitude, title) {
          this.latitude = latitude;
          this.longitude = longitude;
          this.title = title;
        }
      }
      data.forEach(function (element) {
        var exists = false;
        if (self.markerItems.length > 0) {
          self.markerItems.forEach(function (item) {
            if (item.latitude == element.latitude && item.longitude  == element.longitude) {
              exists = true;
              return;
            }
          });
        }
        var stateStr = "Pendiente";
        if (element.state == "done") {
          stateStr = "Listo";
        } else if (element.state == "blocked") {
          stateStr = "Bloqueado";
        }
        var title = "Estado: " + stateStr + "\nFecha y Hora: " + element.date + " " + element.time + "\nObservaciones: " + element.comments + "\nArchivos adjuntos: " + element.task_history_image_ids.length + " archivos.";
        if (!exists) {
          var geoPosition = new GeoPosition(element.latitude, element.longitude, title);
          self.markerItems.push(geoPosition);
        } else {
          var itemSelected = self.markerItems.find(function (item) {
            return item.latitude === element.latitude && item.longitude === element.longitude;
          });
          itemSelected.title += "\n\n" + title;
        }
      });
      self.markerItems.forEach(function (item) {
        var options = {
          map: self.map,
          position: {lat: item.latitude, lng: item.longitude},
          title: item.title,
        };
        var marker = new google.maps.Marker(options);
        self.markers.push(marker);
      });
    },
  });
  field_registry.add('map', MapField);
  return {
    MapField: MapField
  };
});
