import requests
import proto


class LoginError(Exception):
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)


class RequestError(Exception):
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)


class GooglePlayAPI(object):
    """
    Google Play Unofficial API Class

    Usual APIs methods are login(), details(), download().
    """

    LANG = "en_US"
    SERVICE = "androidmarket"
    URL_LOGIN = "https://android.clients.google.com/auth"
    ACCOUNT_TYPE_HOSTED_OR_GOOGLE = "HOSTED_OR_GOOGLE"
    authSubToken = None

    def __init__(self, androidId):
        self.preFetch = {}
        self.androidId = androidId

    def _try_register_preFetch(self, protoObj):
        fields = [i.name for (i, _) in protoObj.ListFields()]
        if ("preFetch" in fields):
            for p in protoObj.preFetch:
                self.preFetch[p.url] = p.response

    def setAuthSubToken(self, authSubToken):
        self.authSubToken = authSubToken

    def login(self, email=None, password=None, authSubToken=None):
        """
        Login to your Google Account. You must provide either:
        - an email and password
        - a valid Google authSubToken
        """
        if (authSubToken is not None):
            self.setAuthSubToken(authSubToken)
        else:
            if (email is None or password is None):
                return False

            params = {"Email": email,
                      "Passwd": password,
                      "service": self.SERVICE,
                      "accountType": self.ACCOUNT_TYPE_HOSTED_OR_GOOGLE,
                      "has_permission": "1",
                      "source": "android",
                      "androidId": self.androidId,
                      "app": "com.android.vending",
                      "device_country": "fr",
                      "operatorCountry": "fr",
                      "lang": "fr",
                      "sdk_version": "16"}

            headers = {
                "Accept-Encoding": "",
            }

            response = requests.post(self.URL_LOGIN, data=params,
                                     headers=headers, verify=False)
            data = response.text.split()
            params = {}
            for d in data:
                try:
                    if "=" not in d:
                        continue
                    s = d.split("=", 1)
                    params[s[0].strip().lower()] = s[1].strip()
                except:
                    return False
            if "auth" in params:
                self.setAuthSubToken(params["auth"])
            elif "error" in params:
                return False
        return True

    def executeRequestApi2(self, path, datapost=None):
        post_content_type = "application/x-www-form-urlencoded; charset=UTF-8"
        if (datapost is None and path in self.preFetch):
            data = self.preFetch[path]
        else:
            headers = {"Accept-Language": self.LANG,
                       "Authorization": "GoogleLogin auth=%s" % self.authSubToken,
                       "X-DFE-Enabled-Experiments": "cl:billing.select_add_instrument_by_default",
                       "X-DFE-Unsupported-Experiments": "nocache:billing.use_charging_poller,market_emails,buyer_currency,prod_baseline,checkin.set_asset_paid_app_field,shekel_test,content_ratings,buyer_currency_in_app,nocache:encrypted_apk,recent_changes",
                       "X-DFE-Device-Id": self.androidId,
                       "X-DFE-Client-Id": "am-android-google",
                       "User-Agent": "Android-Finsky/3.7.13 (api=3,versionCode=8013013,sdk=16,device=crespo,hardware=herring,product=soju)",
                       "X-DFE-SmallestScreenWidthDp": "320",
                       "X-DFE-Filter-Level": "3",
                       "Accept-Encoding": "",
                       "Host": "android.clients.google.com"}

            if datapost is not None:
                headers["Content-Type"] = post_content_type

            url = "https://android.clients.google.com/fdfe/%s" % path
            if datapost is not None:
                response = requests.post(url, data=datapost, headers=headers,
                                         verify=False)
            else:
                response = requests.get(url, headers=headers, verify=False)
            data = response.content

        message = proto.ResponseWrapper.FromString(data)
        self._try_register_preFetch(message)

        return message

    #####################################
    # Google Play API Methods
    #####################################

    def search(self, query, nb_results=None, offset=None):
        """
        Search for apps.
        """
        path = "search?c=3&q=%s" % requests.utils.quote(query)
        if (nb_results is not None):
            path += "&n=%d" % int(nb_results)
        if (offset is not None):
            path += "&o=%d" % int(offset)

        message = self.executeRequestApi2(path)
        return message.payload.searchResponse

    def details(self, packageName):
        """
        Get app details from a package name.
        """
        path = "details?doc=%s" % requests.utils.quote(packageName)
        message = self.executeRequestApi2(path)
        return message.payload.detailsResponse

    def download(self, packageName, versionCode, offerType=1):
        """
        Download an app and return its raw data (APK file).
        """
        path = "purchase"
        data = "ot=%d&doc=%s&vc=%d" % (offerType, packageName, versionCode)
        message = self.executeRequestApi2(path, data)
        status = message.payload.buyResponse.purchaseStatusResponse

        url = status.appDeliveryData.downloadUrl
        cookie = status.appDeliveryData.downloadAuthCookie[0]

        cookies = {
            str(cookie.name): str(cookie.value)
        }

        headers = {"User-Agent": "AndroidDownloadManager/4.1.1 (Linux; U; Android 4.1.1; Nexus S Build/JRO03E)",
                   "Accept-Encoding": ""}

        response = requests.get(url, headers=headers, cookies=cookies, verify=False)
        return response.content
