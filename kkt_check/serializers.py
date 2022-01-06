# Kkt_check/serializers.py
from rest_framework import serializers


class KktSerializer(serializers.Serializer):
    inn_kkt = serializers.CharField(max_length=12)
    fn_number = serializers.CharField(max_length=16)
    cashier_name = serializers.CharField(max_length=100, allow_blank=True, required=False)
    cashier_inn = serializers.CharField(max_length=12, allow_blank=True, required=False)

    def update(self, instance, validated_data):
        instance.inn_kkt = validated_data.get('inn_kkt', instance.inn_kkt)
        instance.fn_number = validated_data.get('fn_number', instance.fn_number)
        instance.cashier_name = validated_data.get('cashier_name', instance.cashier_name)
        instance.cashier_inn = validated_data.get('cashier_inn', instance.cashier_inn)
        instance.save()
        return instance


class CheckSerializer(serializers.Serializer):

    check_num = serializers.IntegerField()
    shft_num = serializers.IntegerField()
    buyer_name = serializers.CharField(max_length=200, allow_blank=True, required=False)
    buyer_inn = serializers.CharField(max_length=12, allow_blank=True, required=False)
    tax_system = serializers.CharField(max_length=1)
    send_check_to = serializers.CharField(max_length=50, allow_blank=True, required=False)
    cash = serializers.IntegerField()
    ecash = serializers.IntegerField()
    status = serializers.CharField(max_length=100)
    date_added = serializers.DateTimeField()


    def update(self, instance, validated_data):

        instance.check_num = validated_data.get('check_num', instance.check_num)
        instance.shft_num = validated_data.get('shft_num', instance.shft_num)
        instance.buyer_name = validated_data.get('buyer_name', instance.buyer_name)
        instance.buyer_inn = validated_data.get('buyer_inn', instance.buyer_inn)
        instance.tax_system = validated_data.get('tax_system', instance.tax_system)
        instance.send_check_to = validated_data.get('send_check_to', instance.send_check_to)
        instance.cash = validated_data.get('cash', instance.cash)
        instance.ecash = validated_data.get('ecash', instance.ecash)
        instance.status = validated_data.get('status', instance.status)
        instance.date_added = validated_data.get('date_added', str(instance.date_added))
        instance.save()
        return instance

class GoodSerializer(serializers.Serializer):

    product_name = serializers.CharField(max_length=200)
    qty = serializers.IntegerField()
    tax_code = serializers.IntegerField()
    price = serializers.IntegerField()
    product_type_code = serializers.IntegerField()