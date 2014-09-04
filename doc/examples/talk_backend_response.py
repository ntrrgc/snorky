if response_obj.status_code != 200:
    print("Non service related error")
else:
    response = json.loads(response.content.decode("UTF-8"))
    # Remove the service envelop
    response = response["message"]
    if response["type"] == "response":
        print("The service replied: " + repr(response["data"]))
    else:
        print("The service signaled an error: " + response["message"])
