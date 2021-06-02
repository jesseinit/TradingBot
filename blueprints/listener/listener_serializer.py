import json
from marshmallow import Schema, fields, post_load, validates
from marshmallow_oneofschema import OneOfSchema

# ? {"coin": "ADA", "trigger1": "TRUE", "trigger2": "TRUE", "trigger3": "TRUE", "trigger4": "TRUE", "price": 1.5001}


class AIDataFiveMinsChartSchema(Schema):
    coin = fields.Str()
    trigger1 = fields.Str()
    trigger2 = fields.Str()
    price = fields.Float()

    @post_load
    def load(self, data, **kwargs):
        return data


class AIDataTwelveHrsChartSchema(Schema):
    coin = fields.Str()
    trigger1 = fields.Str()
    trigger2 = fields.Str()
    trigger3 = fields.Str()
    trigger4 = fields.Str()
    price = fields.Float()

    @post_load
    def load(self, data, **kwargs):
        if "trigger1" in data.keys():
            data['trigger1'] = True if data['trigger1'] == 'TRUE' else False
        if "trigger2" in data.keys():
            data['trigger2'] = True if data['trigger2'] == 'TRUE' else False
        if "trigger3" in data.keys():
            data['trigger3'] = True if data['trigger3'] == 'TRUE' else False
        if "trigger4" in data.keys():
            data['trigger4'] = True if data['trigger4'] == 'TRUE' else False
        return data


class AISchema(OneOfSchema):
    type_schemas = {"five_mins_candle": AIDataFiveMinsChartSchema,
                    "twelve_hrs_candle": AIDataTwelveHrsChartSchema}

# ai_schema = AISchema()
# ai_data_schema = AIDataTwelveHrsChartSchema()
# data = ai_data_schema.dumps({"coin": "ADA", "trigger1": "TRUE", "trigger2": "TRUE",
#                              "trigger3": "TRUE", "trigger4": "TRUE", "price": 1.5001})

# ai_data = ai_schema.load({"type": 'five_mins_chart', "coin": "ADA", "trigger1": "TRUE", "trigger2": "TRUE",
#                           "trigger3": "TRUE", "trigger4": "TRUE", "price": 1.5001})


# print(ai_data)
