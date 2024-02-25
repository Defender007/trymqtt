Pseudo codes
============
::For Subscribers::
def on_message:
    reader_message = message.payload.decode("UTF-8");
    parsed_message = json.dumps(reader_message)
    user_transaction = models.Transaction.objects.filter(reader_uid='1234567',
   date=datetime.now)
    swipe_count = user_transaction.swipe_count
    meal_category = user_transaction.user.meal_category
    if swipe_count < meal_category:
        swipe_count += 1
        user_transaction.swipe_count = swipe_count
        user_transaction.save()
        client.publish(TOPIC, MY_MESSAGE)
    else:
        client.publish(TOPIC, MY_MESSAGE_DENIED)

::URL::
    POST http://localhost:8080/access-control

::HTTP PAYLOAD::
    {"uid": "12345689", "username": "wonder"}

::View::
    class GrantOrRevokeAccess(APIView):
        def post(self, request):
            process_request(request)
            mqtt_payload = {**request.data, **other_data}
            build_mqtt_payload(mqtt_payload)
            log_access_point() #eg. remote,local
            save_data_to_db()
            on_save_signal_event()
        
    def on_save_signal_event():
        publish_access_command_to_mqtt_broker()


::TODO::
    :::add created_by field to Transaction model #eg. admin, owner
    :::add access_point field to Transaction model #eg. remote,local
    :::add a field to dump the raw request data
    :::Generate Transaction Signal to Publish to MQTT Broker
    :::extrat Authentication check steps into a function

    ::create Querysets for filtering, sorting and pagination
    ::create endpoint for daily, weekly, and monthly reports
    ::import from excel file
    ::export to excel file
    ::Barcode or Card Reader

    ::wrap all Api calls in try-catch block in react app
    ::replace all print statements with ic or logger
    ::change the secret key to a production secret
    :::Generate random integer string of 10 characters *rm::
    