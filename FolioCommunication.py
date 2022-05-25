import requests
import json
import os
import logging
from datetime import datetime
from requests.exceptions import HTTPError
from dotenv import load_dotenv


class FolioCommunication:

    def __init__(self):

        # Initialize environment variables
        load_dotenv()
        self.folio_endpoint = os.environ['FOLIO_ENDPOINT']
        self.username = os.environ['FOLIO_USERNAME']
        self.password = os.environ['FOLIO_PASSWORD']
        self.okapi_tenant = os.environ['FOLIO_OKAPI_TENANT']
        self.payload = {'username': self.username,
                        'password': self.password}

        # Define generic header without okapi token
        self.header = {'Accept': 'application/json',
                       'Content-Type': 'application/json',
                       'x-okapi-tenant': self.okapi_tenant}

        # Fetch okapi token
        self.okapi_token = self.getToken()

        # Add okapi token to header
        self.header['x-okapi-token'] = self.okapi_token

    def getToken(self):
        """Method for acquiring OKAPI token."""
        okapiToken = ''
        logging.info('Hämtar okapi token.')
        path = '/authn/login'
        url = self.folio_endpoint + path

        try:
            response = requests.post(url, data=json.dumps(
                self.payload), headers=self.header)
            response.raise_for_status()
            okapiToken = response.headers['x-okapi-token']
            logging.info('Hämtade okapi token: %s', okapiToken)
            return okapiToken
        except HTTPError as http_err:
            logging.error(f'HTTP error occurred: {http_err}')
            return response.status_code
        except Exception as err:
            logging.error(f'Other error occurred: {err}')
            return None

    def uploadDefinitions(self, filename):
        path = '/data-import/uploadDefinitions'
        url = self.folio_endpoint + path
        payload = {'fileDefinitions': [{'name': filename}]}

        try:
            response = requests.post(
                url, data=json.dumps(payload), headers=self.header)
            response.raise_for_status()
            response_json = response.json()
            return response_json
        except HTTPError as http_err:
            logging.error(f'HTTP error occurred: {http_err}')
            return response.status_code
        except Exception as err:
            logging.error(f'Other error occurred: {err}')
            return None

    def uploadFile(self, uploadDefinitionId, fileDefinitionId, data):
        path = '/data-import/uploadDefinitions/' + \
            uploadDefinitionId + '/files/' + fileDefinitionId
        url = self.folio_endpoint + path

        header = {'Content-Type': 'application/octet-stream',
                  'x-okapi-tenant': self.okapi_tenant,
                  'X-Okapi-Token': self.okapi_token}

        try:
            response = requests.post(url, data=data, headers=header)
            response.raise_for_status()
            response_json = response.json()
            return response_json
        except HTTPError as http_err:
            logging.error(f'HTTP error occurred: {http_err}')
            return response.status_code
        except Exception as err:
            logging.error(f'Other error occurred: {err}')
            return None

    def processFile(self, uploadDefinitionId, data):
        path = '/data-import/uploadDefinitions/' + \
            uploadDefinitionId + '/processFiles?defaultMapping=true'
        url = self.folio_endpoint + path

        try:
            response = requests.post(
                url, data=json.dumps(data), headers=self.header)
            return response
        except HTTPError as http_err:
            logging.error(f'HTTP error occurred: {http_err}')
            return response.status_code
        except Exception as err:
            logging.error(f'Other error occurred: {err}')
            return None

    def getMappingRules(self, filename):
        """Method for getting mapping rules, i.e., how MARC21 elements are mapped to internal data. Returns JSON converted to Python dictionary."""
        path = '/mapping-rules'
        url = self.folio_endpoint + path

        try:
            response = requests.get(url, data=json.dumps(
                self.payload), headers=self.header)
            response.raise_for_status()
            response_json = response.json()
            response_json_obejct = json.dumps(response_json)
            logging.info('Systemet säger %s', response.status_code)
            logging.info('Hittade: %s', response_json)
            with open(filename, "w") as outfile:
                outfile.write(response_json_obejct)
            return response_json
        except HTTPError as http_err:
            logging.error(f'HTTP error occurred: {http_err}')
            return response.status_code
        except Exception as err:
            logging.error(f'Other error occurred: {err}')
            return None

    def updateMappingRules(self, mapping_rules):
        """Metod that updates the the mapping rules, i.e., how MARC21 elements are mapped to internal data."""
        path = '/mapping-rules'
        url = self.folio_endpoint + path

        try:
            response = requests.put(
                url, data=json.dumps(mapping_rules), headers=self.header)
            return response
        except HTTPError as http_err:
            logging.error(f'HTTP error occurred: {http_err}')
            return response.status_code
        except Exception as err:
            logging.error(f'Other error occurred: {err}')
            return None

    def restoreMappingRules(self):
        """Method that restores the mapping rules, i.e., how MARC21 elements are mapped to internal data, to original state."""
        path = '/mapping-rules/restore'
        url = self.folio_endpoint + path

        try:
            response = requests.put(
                url, headers=self.header)
            return response
        except HTTPError as http_err:
            logging.error(f'HTTP error occurred: {http_err}')
            return response.status_code
        except Exception as err:
            logging.error(f'Other error occurred: {err}')
            return None


    def getInstance(self, instanceId):
        """Retrieves a specific instance."""
        logging.info(
            'Söker instans: ' + instanceId)
        path = '/instance-storage/instances/' + instanceId
        #path = '/inventory/instances/' + instanceId
        url = self.folio_endpoint + path

        try:
            response = requests.get(url, data=json.dumps(
                self.payload), headers=self.header)
            response.raise_for_status()
            response_json = response.json()
            logging.info('Systemet säger %s', response.status_code)
            logging.info('Hittade: %s',  response_json)
            return response_json
        except HTTPError as http_err:
            logging.error(f'HTTP error occurred: {http_err}')
            return response.status_code
        except Exception as err:
            logging.error(f'Other error occurred: {err}')
            return None

    def getInstances(self, query_string, limit=10):
        """Retrieves instances matching a CQL query string. An optional parameter can be passed to limit how many matches are returned."""
        logging.info(
            'Söker instanser med med följande söksträng: ' + query_string)
        # path = '/inventory/instances'
        path = '/instance-storage/instances'
        url = self.folio_endpoint + path
        # query_string = 'title="' + search_string + '*"'
        param = {'query': query_string, 'limit': limit}
        # the contents under contributors is indexed. accessing it is mindboggling.
        # param = {'query': 'contributors=/@name "Perloff, Marjorie"',
        # 'limit': 10}

        try:
            response = requests.get(url, data=json.dumps(
                self.payload), headers=self.header, params=param)
            response.raise_for_status()
            response_json = response.json()
            logging.info('Systemet säger %s', response.status_code)
            logging.info('Hittade: %s',  response_json)
            return response_json
        except HTTPError as http_err:
            logging.error(f'HTTP error occurred: {http_err}')
            return response.status_code
        except Exception as err:
            logging.error(f'Other error occurred: {err}')
            return None

    def deleteInstance(self, instance_to_delete):
        """Method for deleting instances. Takes a UUID as input. Returns response code. 500 usually means that the instance can not be deleted due to internal constraints being violated."""
        logging.info('Försöker ta bort följande instans: ' +
                     instance_to_delete)
        # path = '/inventory/instances/' + instance_to_delete
        path = '/instance-storage/instances/' + instance_to_delete
        url = self.folio_endpoint + path

        try:
            response = requests.delete(url, data=json.dumps(
                self.payload), headers=self.header)
            logging.info('Systemet säger %s', response.status_code)
            logging.info('Systemet säger %s', response.content)
            return response.status_code
        except HTTPError as http_err:
            logging.error(f'HTTP error occurred: {http_err}')
            return response.status_code
        except Exception as err:
            logging.error(f'Other error occurred: {err}')
            return None

    def getInstanceRelationships(self, limit=10):
        logging.info('Hämtar instance relationships.')
        path = '/instance-storage/instance-relationships'
        url = self.folio_endpoint + path
        
        param = {'limit': limit}
        
        try:
            response = requests.get(url, data=json.dumps(
                self.payload), headers=self.header, params=param)
            response.raise_for_status()
            response_json = response.json()
            logging.info('Systemet säger %s', response.status_code)
            logging.info('Hittade: %s',  response_json)
            return response_json
        except HTTPError as http_err:
            logging.error(f'HTTP error occurred: {http_err}')
            return response.status_code
        except Exception as err:
            logging.error(f'Other error occurred: {err}')
            return None

    def deleteInstanceRelationships(self, instance_to_delete):
        logging.info('Försöker ta bort instance relationship: ' +
                     instance_to_delete)
        path = '/instance-storage/instance-relationships/' + instance_to_delete
        url = self.folio_endpoint + path

        local_header = self.header
        local_header['Accept'] = 'text/plain'

        try:
            response = requests.delete(url, data=json.dumps(
                self.payload), headers=local_header)
            logging.info('Systemet säger %s', response.status_code)
            logging.debug('Systemet säger %s', response.content)
            return response.status_code
        except HTTPError as http_err:
            logging.error(f'HTTP error occurred: {http_err}')
            return response.status_code
        except Exception as err:
            logging.error(f'Other error occurred: {err}')
            return None

    def getSourceRecords(self, limit=10, deleted=False):
        logging.info('Hämtar source records.')
        path = '/source-storage/source-records'
        url = self.folio_endpoint + path
        
        param = {'limit': limit, 'deleted': deleted}
        
        try:
            response = requests.get(url, data=json.dumps(
                self.payload), headers=self.header, params=param)
            response.raise_for_status()
            response_json = response.json()
            logging.info('Systemet säger %s', response.status_code)
            logging.info('Hittade: %s',  response_json)
            return response_json
        except HTTPError as http_err:
            logging.error(f'HTTP error occurred: {http_err}')
            return response.status_code
        except Exception as err:
            logging.error(f'Other error occurred: {err}')
            return None

    def getSRSRecordId(self, instance_uuid):
        logging.info('Hämtar SRS uuid för instans: ' +
                     instance_uuid)
        path = '/source-storage/records/' + instance_uuid + '/formatted?idType=INSTANCE'
        url = self.folio_endpoint + path

        try:
            response = requests.get(url, data=json.dumps(
                self.payload), headers=self.header)
            response.raise_for_status()
            response_json = response.json()
            logging.info('Systemet säger %s', response.status_code)
            logging.debug('Systemet säger %s', response.content)
            return response_json['id']
        except HTTPError as http_err:
            logging.error(f'HTTP error occurred: {http_err}')
            return response.status_code
        except Exception as err:
            logging.error(f'Other error occurred: {err}')
            return None

    def deleteSRSRecord(self, instance_to_delete):
        logging.info('Försöker ta bort source record: ' +
                     instance_to_delete)
        # path = '/inventory/instances/' + instance_to_delete
        # path = '/instance-storage/instances/' + \
        #     instance_to_delete + '/source-record/marc-json'
        path = '/source-storage/records/' + instance_to_delete
        #path = '/instance-storage/instances/' + instance_to_delete + "/source-record"
        url = self.folio_endpoint + path

        local_header = self.header
        local_header['Accept'] = 'text/plain'

        try:
            response = requests.delete(url, data=json.dumps(
                self.payload), headers=local_header)
            logging.info('Systemet säger %s', response.status_code)
            logging.debug('Systemet säger %s', response.content)
            return response.status_code
        except HTTPError as http_err:
            logging.error(f'HTTP error occurred: {http_err}')
            return response.status_code
        except Exception as err:
            logging.error(f'Other error occurred: {err}')
            return None

    def deleteLoans(self):
        logging.info('Tar bort alla lån.')
        path = '/loan-storage/loans'
        url = self.folio_endpoint + path

        local_header = self.header
        local_header['Accept'] = 'text/plain'

        try:
            response = requests.delete(url, data=json.dumps(
                self.payload), headers=local_header)
            logging.info('Systemet säger %s', response.status_code)
            logging.debug('Systemet säger %s', response.content)
            return response.status_code
        except HTTPError as http_err:
            logging.error(f'HTTP error occurred: {http_err}')
            return response.status_code
        except Exception as err:
            logging.error(f'Other error occurred: {err}')
            return None

    def deleteRequests(self):
        logging.info('Tar bort alla reservationer.')
        path = '/request-storage/requests'
        url = self.folio_endpoint + path

        local_header = self.header
        local_header['Accept'] = 'text/plain'

        try:
            response = requests.delete(url, data=json.dumps(
                self.payload), headers=local_header)
            logging.info('Systemet säger %s', response.status_code)
            logging.debug('Systemet säger %s', response.content)
            return response.status_code
        except HTTPError as http_err:
            logging.error(f'HTTP error occurred: {http_err}')
            return response.status_code
        except Exception as err:
            logging.error(f'Other error occurred: {err}')
            return None

    def getCirculationLog(self, limit=10):
        path = '/audit-data/circulation/logs'
        url = self.folio_endpoint + path
        
        param = {'limit': limit}
        
        try:
            response = requests.get(url, data=json.dumps(
                self.payload), headers=self.header, params=param)
            response.raise_for_status()
            response_json = response.json()
            logging.info('Systemet säger %s', response.status_code)
            logging.info('Hittade: %s',  response_json)
            return response_json
        except HTTPError as http_err:
            logging.error(f'HTTP error occurred: {http_err}')
            return response.status_code
        except Exception as err:
            logging.error(f'Other error occurred: {err}')
            return None

    def deleteCirculationLog(self):
        logging.info('Tar bort circulation log.')
        path = '/audit-data/circulation/logs'
        url = self.folio_endpoint + path

        local_header = self.header
        local_header['Accept'] = 'text/plain'

        try:
            response = requests.delete(url, data=json.dumps(
                self.payload), headers=local_header)
            logging.info('Systemet säger %s', response.status_code)
            logging.debug('Systemet säger %s', response.content)
            return response.status_code
        except HTTPError as http_err:
            logging.error(f'HTTP error occurred: {http_err}')
            return response.status_code
        except Exception as err:
            logging.error(f'Other error occurred: {err}')
            return None



    def getItems(self, query_string, limit=10):
        """Retrieves items matching a CQL query string. An optional parameter can be passed to limit how many matches are returned."""
        logging.info(
            'Söker items med med följande söksträng: ' + query_string)
        #path = '/inventory/items'
        path = '/item-storage/items'
        url = self.folio_endpoint + path
        # query_string = 'title="' + search_string + '*"'
        param = {'query': query_string, 'limit': limit}
        # the contents under contributors is indexed. accessing it is mindboggling.
        # param = {'query': 'contributors=/@name "Perloff, Marjorie"',
        # 'limit': 10}

        try:
            response = requests.get(url, data=json.dumps(
                self.payload), headers=self.header, params=param)
            response.raise_for_status()
            response_json = response.json()
            logging.info('Systemet säger %s', response.status_code)
            logging.info('Hittade: %s',  response_json)
            return response_json
        except HTTPError as http_err:
            logging.error(f'HTTP error occurred: {http_err}')
            return response.status_code
        except Exception as err:
            logging.error(f'Other error occurred: {err}')
            return None

    def deleteItem(self, uuid):
        logging.info('Försöker ta bort följande item: ' +
                     uuid)
        path = '/item-storage/items/' + uuid
        url = self.folio_endpoint + path

        local_header = self.header
        local_header['Accept'] = 'text/plain'

        try:
            response = requests.delete(url, data=json.dumps(
                self.payload), headers=local_header)
            logging.info('Systemet säger %s', response.status_code)
            logging.info('Systemet säger %s', response.content)
            return response.status_code
        except HTTPError as http_err:
            logging.error(f'HTTP error occurred: {http_err}')
            return response.status_code
        except Exception as err:
            logging.error(f'Other error occurred: {err}')
            return None

    def updateItem(self, itemId, itemData):
        """Update a specific holdings with callNumberSuffix"""
        path = '/inventory/items/' + itemId
        url = self.folio_endpoint + path

        try:
            response = requests.put(
                url, data=json.dumps(itemData), headers=self.header)
            return response
        except HTTPError as http_err:
            logging.error(f'HTTP error occurred: {http_err}')
            return response.status_code
        except Exception as err:
            logging.error(f'Other error occurred: {err}')
            return None

    def getLocations(self):
                
        path = '/locations'
        url = self.folio_endpoint + path
        
        param = {'limit': 300}
        
        try:
            response = requests.get(url, data=json.dumps(
                self.payload), headers=self.header, params=param)
            response.raise_for_status()
            response_json = response.json()
            logging.info('Systemet säger %s', response.status_code)
            logging.info('Hittade: %s',  response_json)
            return response_json
        except HTTPError as http_err:
            logging.error(f'HTTP error occurred: {http_err}')
            return response.status_code
        except Exception as err:
            logging.error(f'Other error occurred: {err}')
            return None

    def getLoans(self, limit=10):
                
        path = '/circulation/loans'
        url = self.folio_endpoint + path
        
        param = {'limit': limit}
        
        try:
            response = requests.get(url, data=json.dumps(
                self.payload), headers=self.header, params=param)
            response.raise_for_status()
            response_json = response.json()
            logging.info('Systemet säger %s', response.status_code)
            logging.info('Hittade: %s',  response_json)
            return response_json
        except HTTPError as http_err:
            logging.error(f'HTTP error occurred: {http_err}')
            return response.status_code
        except Exception as err:
            logging.error(f'Other error occurred: {err}')
            return None



    def getHolds(self, query):
        
        path = '/circulation/requests'
        url = self.folio_endpoint + path
        
        param = {'query': query, 'limit': 500}
        
        try:
            response = requests.get(url, data=json.dumps(
                self.payload), headers=self.header, params=param)
            response.raise_for_status()
            response_json = response.json()
            logging.info('Systemet säger %s', response.status_code)
            logging.info('Hittade: %s',  response_json)
            return response_json
        except HTTPError as http_err:
            logging.error(f'HTTP error occurred: {http_err}')
            return response.status_code
        except Exception as err:
            logging.error(f'Other error occurred: {err}')
            return None

    def moveHold(self, requestId, itemId, requestType):
        path = '/circulation/requests/' + requestId + '/move'

        url = self.folio_endpoint + path
        payload = {'destinationItemId': itemId, 'requestType': requestType }

        try:
            response = requests.post(
                url, data=json.dumps(payload), headers=self.header)
            response.raise_for_status()
            response_json = response.json()
            return response_json
        except HTTPError as http_err:
            logging.error(f'HTTP error occurred: {http_err}')
            return response.status_code
        except Exception as err:
            logging.error(f'Other error occurred: {err}')
            return None


    def getData(self, path, query, limit):
        
        url = self.folio_endpoint + path
        param = {'query': query, 'limit': limit}
        
        try:
            response = requests.get(url, data=json.dumps(
                self.payload), headers=self.header, params=param)
            response.raise_for_status()
            response_json = response.json()
            logging.info('Systemet säger %s', response.status_code)
            logging.info('Hittade: %s',  response_json)
            return response_json
        except HTTPError as http_err:
            logging.error(f'HTTP error occurred: {http_err}')
            return response.status_code
        except Exception as err:
            logging.error(f'Other error occurred: {err}')
            return None

    def postData(self, path, payload):
        
        url = self.folio_endpoint + path
        
        try:
            response = requests.post(
                url, data=payload, headers=self.header)
            response.raise_for_status()
            # response_json = response.json()
            return response
        except HTTPError as http_err:
            logging.error(f'HTTP error occurred: {http_err}')
            return response.status_code
        except Exception as err:
            logging.error(f'Other error occurred: {err}')
            return None

    def putUserData(self, path, payload):
        
        url = self.folio_endpoint + path
        local_header = self.header
        local_header['Accept'] = 'text/plain'

        
        try:
            response = requests.put(
                url, data=payload, headers=local_header)
            response.raise_for_status()
            # response_json = response.json()
            return response
        except HTTPError as http_err:
            logging.error(f'HTTP error occurred: {http_err}')
            return response.status_code
        except Exception as err:
            logging.error(f'Other error occurred: {err}')
            return None


    def getCallNumberTypes(self):
                
        path = '/call-number-types'
        url = self.folio_endpoint + path
        
        param = {'limit': 20}
        
        try:
            response = requests.get(url, data=json.dumps(
                self.payload), headers=self.header, params=param)
            response.raise_for_status()
            response_json = response.json()
            logging.info('Systemet säger %s', response.status_code)
            logging.info('Hittade: %s',  response_json)
            return response_json
        except HTTPError as http_err:
            logging.error(f'HTTP error occurred: {http_err}')
            return response.status_code
        except Exception as err:
            logging.error(f'Other error occurred: {err}')
            return None


    def getPrecedingSucceedingTitles(self, limit=10):
        path = '/preceding-succeeding-titles'
        url = self.folio_endpoint + path
        param = {'limit': limit}
        
        try:
            response = requests.get(url, data=json.dumps(
                self.payload), headers=self.header, params=param)
            response.raise_for_status()
            response_json = response.json()
            logging.info('Systemet säger %s', response.status_code)
            logging.info('Hittade: %s',  response_json)
            return response_json
        except HTTPError as http_err:
            logging.error(f'HTTP error occurred: {http_err}')
            return response.status_code
        except Exception as err:
            logging.error(f'Other error occurred: {err}')
            return None


    def deletePrecedingSucceedingTitle(self, precedingSucceedingTitleId):
        logging.info('Försöker ta bort följande precedingSucceeding titel: ' +
                     precedingSucceedingTitleId)
        path = '/preceding-succeeding-titles/' + precedingSucceedingTitleId
        url = self.folio_endpoint + path

        local_header = self.header
        local_header['Accept'] = 'text/plain'

        try:
            response = requests.delete(url, data=json.dumps(
                self.payload), headers=self.header)
            logging.info('Systemet säger %s', response.status_code)
            logging.info('Systemet säger %s', response.content)
            return response.status_code
        except HTTPError as http_err:
            logging.error(f'HTTP error occurred: {http_err}')
            return response.status_code
        except Exception as err:
            logging.error(f'Other error occurred: {err}')
            return None

    def getMaterialTypes(self):
        path = '/material-types'
        url = self.folio_endpoint + path
        param = {'limit': 100}

        try:
            response = requests.get(url, data=json.dumps(
                self.payload), headers=self.header, params=param)
            response.raise_for_status()
            response_json = response.json()
            logging.info('Systemet säger %s', response.status_code)
            logging.info('Hittade: %s', response_json)
            return response_json
        except HTTPError as http_err:
            logging.error(f'HTTP error occurred: {http_err}')
            return response.status_code
        except Exception as err:
            logging.error(f'Other error occurred: {err}')
            return None

    
    def getLoanTypes(self):
        path = '/loan-types'
        url = self.folio_endpoint + path
        param = {'limit': 200}

        try:
            response = requests.get(url, data=json.dumps(
                self.payload), headers=self.header, params=param)
            response.raise_for_status()
            response_json = response.json()
            logging.info('Systemet säger %s', response.status_code)
            logging.info('Hittade: %s', response_json)
            return response_json
        except HTTPError as http_err:
            logging.error(f'HTTP error occurred: {http_err}')
            return response.status_code
        except Exception as err:
            logging.error(f'Other error occurred: {err}')
            return None


    def userExists(self, username):
        path = '/users?limit=1&query=(username=$' + username + ')'
        url = self.folio_endpoint + path

        try:
            response = requests.get(url, data=json.dumps(
                self.payload), headers=self.header)
            response.raise_for_status()
            response_json = response.json()
            logging.info('Systemet säger %s', response.status_code)
            logging.info('Resultat: %s', response_json)
            if response_json['totalRecords'] > 0:
                return response_json
            else:
                return False
        except HTTPError as http_err:
            logging.error(f'HTTP error occurred: {http_err}')
            return response.status_code
        except Exception as err:
            logging.error(f'Other error occurred: {err}')
            return None

    def getUserUUID(self, user):
        if user['totalRecords'] > 1:
            logging.info(
                'Det finns fler än en användare i indata. Kan inte hämta unikt UUID')
            return None
        else:
            return user['users'][0]['id']

    def getAddressTypes(self):
        path = '/addresstypes'
        url = self.folio_endpoint + path
        param = {'limit': 100}

        try:
            response = requests.get(url, data=json.dumps(
                self.payload), headers=self.header, params=param)
            response.raise_for_status()
            response_json = response.json()
            logging.info('Systemet säger %s', response.status_code)
            logging.info('Hittade: %s', response_json)
            return response_json
        except HTTPError as http_err:
            logging.error(f'HTTP error occurred: {http_err}')
            return response.status_code
        except Exception as err:
            logging.error(f'Other error occurred: {err}')
            return None

    def getAddressTypeUUID(self, address_types, address_type):
        result = None

        for item in address_types['addressTypes']:
            if item['addressType'] == address_type:
                result = item['id']

        return result

    def runAgedToLost(self):
        path = "/circulation/scheduled-age-to-lost"
        url = self.folio_endpoint + path

        try:
            response = requests.post(url, headers=self.header)
            response.raise_for_status()

            logging.info('Systemet säger %s', response.status_code)

            return response.status_code
        except HTTPError as http_err:
            logging.error(f'HTTP error occurred: {http_err}')
            return response.status_code
        except Exception as err:
            logging.error(f'Other error occurred: {err}')
            return None

    def runAgedToLostFeeCharging(self):
        path = "/circulation/scheduled-age-to-lost-fee-charging"
        url = self.folio_endpoint + path

        try:
            response = requests.post(url, headers=self.header)
            response.raise_for_status()

            logging.info('Systemet säger %s', response.status_code)

            return response.status_code
        except HTTPError as http_err:
            logging.error(f'HTTP error occurred: {http_err}')
            return response.status_code
        except Exception as err:
            logging.error(f'Other error occurred: {err}')
            return None

    def checkOutByBarcode(self, itemBarcode, userBarcode, servicePointId):

        path = "/circulation/check-out-by-barcode"
        url = self.folio_endpoint + path

        payload = {"itemBarcode": itemBarcode,
                   "userBarcode": userBarcode,
                   "servicePointId": servicePointId}

        # CheckOut:

        try:
            response = requests.post(
                url, data=json.dumps(payload), headers=self.header)
            logging.info('Systemet säger %s', response.content)
            response.raise_for_status()
            response_json = response.json()
            logging.info('Systemet säger %s', response.status_code)
            logging.info('Systemet säger %s', response_json)
            return response_json
        except HTTPError as http_err:
            logging.error(f'HTTP error occurred: {http_err}')
            return response.status_code
        except Exception as err:
            logging.error(f'Other error occurred: {err}')
            return None

    def renewByBarcode(self, itemBarcode, userBarcode):

        path = "/circulation/renew-by-barcode"
        url = self.folio_endpoint + path

        payload = {"itemBarcode": itemBarcode,
                   "userBarcode": userBarcode}

        try:
            response = requests.post(
                url, data=json.dumps(payload), headers=self.header)
            logging.info('Systemet säger %s', response.content)
            response.raise_for_status()
            response_json = response.json()
            logging.info('Systemet säger %s', response.status_code)
            logging.info('Systemet säger %s', response_json)
            return response_json
        except HTTPError as http_err:
            logging.error(f'HTTP error occurred: {http_err}')
            return response.status_code
        except Exception as err:
            logging.error(f'Other error occurred: {err}')
            return None

    def getLoansByDueDate(self, dueDateFrom, dueDateTo):
        path = '/circulation/loans?limit=1000&query=(dueDate>="' + dueDateFrom + \
            '" and dueDate<="' + dueDateTo + '" and status.name==Open)'
        url = self.folio_endpoint + path
        #param = {'query':(status.name == 'Open'),'limit': 1000}

        try:
            response = requests.get(url, data=json.dumps(
                self.payload), headers=self.header)
            response.raise_for_status()
            response_json = response.json()
            logging.info('Systemet säger %s', response.status_code)
            logging.info('Hittade: %s', response_json)
            return response_json
        except HTTPError as http_err:
            logging.error(f'HTTP error occurred: {http_err}')
            return response.status_code
        except Exception as err:
            logging.error(f'Other error occurred: {err}')
            return None

    def getGroups(self):
        path = '/groups'
        url = self.folio_endpoint + path
        param = {'limit': 100}

        try:
            response = requests.get(url, data=json.dumps(
                self.payload), headers=self.header, params=param)
            response.raise_for_status()
            response_json = response.json()
            logging.info('Systemet säger %s', response.status_code)
            logging.info('Hittade: %s', response_json)
            return response_json
        except HTTPError as http_err:
            logging.error(f'HTTP error occurred: {http_err}')
            return response.status_code
        except Exception as err:
            logging.error(f'Other error occurred: {err}')
            return None

    def createUser(self, user_dict, patron_group_uuid, address_type_uuid):
        logging.info('Försöker skapa användare %s', user_dict['id'])
        date = str(datetime.now())[0:10]

        path = '/users'
        url = self.folio_endpoint + path
        payload = {'username': user_dict['id'],
                   'externalSystemId': user_dict['id'],
                   'patronGroup': patron_group_uuid,
                   'active': 'true',
                   'personal': {
            'firstName': user_dict['name'],
            'middleName': user_dict['co1'],
            'lastName': user_dict['co2'],
            'email': user_dict['email'],
            'dateOfBirth': '1900-12-01',
            'addresses': [{
                'countryId': 'SE',
                'addressLine1': user_dict['street_address'],
                'addressLine2': user_dict['po_box'],
                'city': user_dict['city'],
                'postalCode': user_dict['postal_code'],
                'addressTypeId': address_type_uuid,
                'primaryAddress': 'true'
            }],
            'preferredContactTypeId': '002',
        },
            'expirationDate': '2022-12-31',
            'enrollmentDate': date,
            'barcode': user_dict['id']
        }

        try:
            response = requests.post(
                url, data=json.dumps(payload), headers=self.header)
            logging.info('Systemet säger %s', response.content)
            response.raise_for_status()
            response_json = response.json()
            logging.info('Systemet säger %s', response.status_code)
            logging.info('Systemet säger %s', response_json)
            return response_json
        except HTTPError as http_err:
            logging.error(f'HTTP error occurred: {http_err}')
            return response.status_code
        except Exception as err:
            logging.error(f'Other error occurred: {err}')
            return None

    def deleteUser(self, user_to_delete):
        logging.info('Försöker ta bort följande användare: ' +
                     user_to_delete)
        path = '/users/' + user_to_delete
        url = self.folio_endpoint + path

        header = {'Content-Type': 'application/json',
                  'Accept': 'text/plain',
                  'x-okapi-tenant': self.okapi_tenant,
                  'X-Okapi-Token': self.okapi_token}

        try:
            response = requests.delete(url, data=json.dumps(
                self.payload), headers=header)
            logging.info('Systemet säger %s', response.status_code)
            return response.status_code
        except HTTPError as http_err:
            logging.error(f'HTTP error occurred: {http_err}')
            return response.status_code
        except Exception as err:
            logging.error(f'Other error occurred: {err}')
            return None

    def importUsers(self, users):
        logging.info('Försöker importera användare')
        date = str(datetime.now())[0:10]

        path = '/user-import'
        url = self.folio_endpoint + path

        try:
            response = requests.post(
                url, headers=self.header, json=users)
            logging.info('Systemet säger %s', response.content)
            response.raise_for_status()
            response_json = response.json()
            logging.info('Systemet säger %s', response.status_code)
            logging.info('Systemet säger %s', response_json)
            return response_json
        except HTTPError as http_err:
            logging.error(f'HTTP error occurred: {http_err}')
            return response.status_code
        except Exception as err:
            logging.error(f'Other error occurred: {err}')
            return None

    def getLocations(self):
        path = '/locations'
        url = self.folio_endpoint + path
        param = {'limit': 1000}

        try:
            response = requests.get(url, data=json.dumps(
                self.payload), headers=self.header, params=param)
            response.raise_for_status()
            response_json = response.json()
            logging.info('Systemet säger %s', response.status_code)
            logging.info('Hittade: %s', response_json)
            return response_json
        except HTTPError as http_err:
            logging.error(f'HTTP error occurred: {http_err}')
            return response.status_code
        except Exception as err:
            logging.error(f'Other error occurred: {err}')
            return None

    def getHoldingsStorage(self, query_string, limit=10):
        path = '/holdings-storage/holdings'
        url = self.folio_endpoint + path
        param = {'query': query_string, 'limit': limit}

        try:
            response = requests.get(url, data=json.dumps(
                self.payload), headers=self.header, params=param)
            response.raise_for_status()
            response_json = response.json()
            logging.info('Systemet säger %s', response.status_code)
            logging.info('Hittade: %s', response_json)
            return response_json
        except HTTPError as http_err:
            logging.error(f'HTTP error occurred: {http_err}')
            return response.status_code
        except Exception as err:
            logging.error(f'Other error occurred: {err}')
            return None

    def getHoldings(self, holdingId):
        path = '/holdings-storage/holdings/' + holdingId 
        url = self.folio_endpoint + path

        try:
            response = requests.get(url, data=json.dumps(
                self.payload), headers=self.header)
            response.raise_for_status()
            response_json = response.json()
            logging.info('Systemet säger %s', response.status_code)
            logging.info('Hittade: %s', response_json)
            return response_json
        except HTTPError as http_err:
            logging.error(f'HTTP error occurred: {http_err}')
            return response.status_code
        except Exception as err:
            logging.error(f'Other error occurred: {err}')
            return None

    def updateHoldings(self, holdingsId, holdingsData):
        """Update a specific holdings with callNumberSuffix"""
        #path = '/inventory/holdings/' + holdingsId
        path = '/holdings-storage/holdings/' + holdingsId
        url = self.folio_endpoint + path

        local_header = self.header
        local_header['Accept'] = 'text/plain'

        try:
            response = requests.put(
                url, data=json.dumps(holdingsData), headers=self.header)
            logging.error('Systemet säger %s', response.content)
            return response
        except HTTPError as http_err:
            logging.error(f'HTTP error occurred: {http_err}')
            return response.status_code
        except Exception as err:
            logging.error(f'Other error occurred: {err}')
            return None

    def deleteHoldingsRecord(self, uuid):
        logging.info('Försöker ta bort följande holdings: ' +
                     uuid)
        path = '/holdings-storage/holdings/' + uuid
        url = self.folio_endpoint + path

        local_header = self.header
        local_header['Accept'] = 'text/plain'

        try:
            response = requests.delete(url, data=json.dumps(
                self.payload), headers=local_header)
            logging.info('Systemet säger %s', response.status_code)
            logging.info('Systemet säger %s', response.content)
            return response.status_code
        except HTTPError as http_err:
            logging.error(f'HTTP error occurred: {http_err}')
            return response.status_code
        except Exception as err:
            logging.error(f'Other error occurred: {err}')
            return None

    def importHoldings(self, holdingsRecord):
        
        path = '/holdings-storage/batch/synchronous'
        url = self.folio_endpoint + path

        try:

            response = requests.post(
                url, data=holdingsRecord, headers=self.header)
            logging.info('Systemet säger %s', response.content)
            response.raise_for_status()
            
            logging.info('Systemet säger %s', response.status_code)

            return response

        except HTTPError as http_err:
            logging.error(f'HTTP error occurred: {http_err}')
            return response.status_code
        except Exception as err:
            logging.error(f'Other error occurred: {err}')
            return None


    def importItems(self, items):
        
        path = '/item-storage/batch/synchronous'
        url = self.folio_endpoint + path
        header = self.header

        try:
            response = requests.post(
                url, headers=header, data=items)
            logging.info('Systemet säger %s', response.content)
            response.raise_for_status()
            
            logging.info('Systemet säger %s', response.status_code)
            
            return response

        except HTTPError as http_err:
            logging.error(f'HTTP error occurred: {http_err}')
            return response.status_code
        except Exception as err:
            logging.error(f'Other error occurred: {err}')
            return None


    def getUserId(self, username):

        path = '/users?limit=1&query=(username=' + username + ')'
        url = self.folio_endpoint + path

        header = {'Accept': 'application/json',
                    'Content-Type': 'application/json',
                    'x-okapi-tenant': self.okapi_tenant,
                    'x-okapi-token': self.okapiToken}

        try:
            response = requests.get(
                url, headers=header)
            logging.info('Systemet säger %s', response.content)
            response.raise_for_status()
            response_json = response.json()
            logging.info('Systemet säger %s', response.status_code)
            logging.info('Systemet säger %s', response_json)


            if response_json['resultInfo']['totalRecords'] == 0:
                userId = ""
            else:
                userId = response_json['users'][0]['id']

            return userId

        except HTTPError as http_err:
            logging.error(f'HTTP error occurred: {http_err}')
            return response.status_code
        except Exception as err:
            logging.error(f'Other error occurred: {err}')
            return None

    def addNewPermissions(self, userId):

        path = '/perms/users'  

        jsondata = {'userId': userId,
                    'permissions': ['patron.all','users.collection.get','circulation.requests.item.get']
                     }

        url = self.folio_endpoint + path

        header = {'Accept': 'application/json',
                    'Content-Type': 'application/json',
                    'x-okapi-tenant': self.okapi_tenant,
                    'x-okapi-token': self.okapiToken}

        try:
            response = requests.post(
                url, headers=header, json=jsondata)
            logging.info('Systemet säger %s', response.content)
            response.raise_for_status()
            response_json = response.json()
            logging.info('Systemet säger %s', response.status_code)
            logging.info('Systemet säger %s', response_json)
            return response_json
        except HTTPError as http_err:
            logging.error(f'HTTP error occurred: {http_err}')
            return response.status_code
        except Exception as err:
            logging.error(f'Other error occurred: {err}')
            return None

    def setExistingPermissions(self, permissionsId, userId, permissions):

        path = '/perms/users/' + permissionsId

        jsondata = {'id': permissionsId,
                    'userId': userId,
                    'permissions': permissions
                     }

        url = self.folio_endpoint + path

        header = {'Accept': 'application/json',
                    'Content-Type': 'application/json',
                    'x-okapi-tenant': self.okapi_tenant,
                    'x-okapi-token': self.okapiToken}

        try:
            response = requests.put(
                url, headers=header, json=jsondata)
            logging.info('Systemet säger %s', response.content)
            response.raise_for_status()
            response_json = response.json()
            logging.info('Systemet säger %s', response.status_code)
            logging.info('Systemet säger %s', response_json)
            return response_json
        except HTTPError as http_err:
            logging.error(f'HTTP error occurred: {http_err}')
            return response.status_code
        except Exception as err:
            logging.error(f'Other error occurred: {err}')
            return None


    def getPermissionsId(self, userId):

        path = '/perms/users?query=userId=' + userId
        url = self.folio_endpoint + path

        header = {'Accept': 'application/json',
                    'Content-Type': 'application/json',
                    'x-okapi-tenant': self.okapi_tenant,
                    'x-okapi-token': self.okapiToken}

        try:
            response = requests.get(
                url, headers=header)
            logging.info('Systemet säger %s', response.content)
            response.raise_for_status()
            response_json = response.json()
            logging.info('Systemet säger %s', response.status_code)
            logging.info('Systemet säger %s', response_json)


            if response_json['resultInfo']['totalRecords'] == 0:
                result = ""
            else:
                result = response_json['permissionUsers'][0]['id']

            return result

        except HTTPError as http_err:
            logging.error(f'HTTP error occurred: {http_err}')
            return response.status_code
        except Exception as err:
            logging.error(f'Other error occurred: {err}')
            return None


    def PIN_Exists(self, userId):
    
        path = '/authn/credentials-existence?userId=' + userId
        url = self.folio_endpoint + path

        header = {'Accept': 'application/json',
                    'Content-Type': 'application/json',
                    'x-okapi-tenant': self.okapi_tenant,
                    'x-okapi-token': self.okapiToken}

        try:
            response = requests.get(
                url, headers=header)
            logging.info('Systemet säger %s', response.content)
            response.raise_for_status()
            response_json = response.json()
            logging.info('Systemet säger %s', response.status_code)
            logging.info('Systemet säger %s', response_json)

            result = response_json['credentialsExist']

            return result

        except HTTPError as http_err:
            logging.error(f'HTTP error occurred: {http_err}')
            return response.status_code
        except Exception as err:
            logging.error(f'Other error occurred: {err}')
            return None



    def removePIN(self, userId):
        
        path = '/authn/credentials?userId=' + userId
        url = self.folio_endpoint + path

        header = {'Accept': 'application/json',
                    'Content-Type': 'application/json',
                    'x-okapi-tenant': self.okapi_tenant,
                    'x-okapi-token': self.okapiToken}

        try:
            response = requests.delete(
                url, headers=header)
            logging.info('Systemet säger %s', response.content)
            response.raise_for_status()
    
            logging.info('Systemet säger %s', response.status_code)

            return response

        except HTTPError as http_err:
            logging.error(f'HTTP error occurred: {http_err}')
            return response.status_code
        except Exception as err:
            logging.error(f'Other error occurred: {err}')
            return None


    def setPIN(self, userId, pin):
        
        path = '/authn/credentials'

        jsondata = {'userId': userId,
                    'password': pin
                     }

        url = self.folio_endpoint + path

        header = {'Accept': 'application/json',
                    'Content-Type': 'application/json',
                    'x-okapi-tenant': self.okapi_tenant,
                    'x-okapi-token': self.okapiToken}

        try:
            response = requests.post(
                url, headers=header, json=jsondata)
            logging.info('Systemet säger %s', response.content)
            response.raise_for_status()
            
            logging.info('Systemet säger %s', response.status_code)
            
            return response

        except HTTPError as http_err:
            logging.error(f'HTTP error occurred: {http_err}')
            return response.status_code
        except Exception as err:
            logging.error(f'Other error occurred: {err}')
            return None

    def deleteServicePoint(self, uuid):
        logging.info('Försöker ta bort följande service point: ' +
                     uuid)
        path = '/service-points/' + uuid
        url = self.folio_endpoint + path

        local_header = self.header
        local_header['Accept'] = 'text/plain'

        try:
            response = requests.delete(url, data=json.dumps(
                self.payload), headers=local_header)
            logging.info('Systemet säger %s', response.status_code)
            logging.info('Systemet säger %s', response.content)
            return response.status_code
        except HTTPError as http_err:
            logging.error(f'HTTP error occurred: {http_err}')
            return response.status_code
        except Exception as err:
            logging.error(f'Other error occurred: {err}')
            return None

    def getConfigurationsAudit(self):
        path = '/configurations/audit' 
        url = self.folio_endpoint + path

        try:
            response = requests.get(url, data=json.dumps(
                self.payload), headers=self.header)
            response.raise_for_status()
            response_json = response.json()
            logging.info('Systemet säger %s', response.status_code)
            logging.info('Hittade: %s', response_json)
            return response_json
        except HTTPError as http_err:
            logging.error(f'HTTP error occurred: {http_err}')
            return response.status_code
        except Exception as err:
            logging.error(f'Other error occurred: {err}')
            return None



def demo_libris_import(folio):
    for filename in os.listdir("../libris_files/"):
        if filename.endswith(".mrc"):
            if os.stat("../libris_files/" + filename).st_size != 0:

                stage1_result = folio.uploadDefinitions(filename)
                print("STAGE 1:", stage1_result)
                uploadDefinitionId = stage1_result['id']
                fileDefinitionId = stage1_result['fileDefinitions'][0]['id']

                with open("../libris_files/" + filename, 'rb') as f:
                    data = f.read()

                stage2_result = folio.uploadFile(
                    uploadDefinitionId, fileDefinitionId, data)
                print("STAGE 2", stage2_result)

                stage2_string = json.dumps(stage2_result)
                stage2_string = stage2_string.replace("'", '"')

                data = '{"uploadDefinition":' + stage2_string + \
                    ', "jobProfileInfo": {"id": "aa8ff044-2490-4611-ac74-3054aa21e8eb", "name": "Libris", "dataType": "MARC"}}'
                data_json = json.loads(data)

                stage3_result = folio.processFile(
                    uploadDefinitionId, data_json)
                print("STAGE 3:", stage3_result)


def demo_update_mapping_rules(folio):
    # logging.info('Hämtar mappningsregler.')
    folio.getMappingRules("../data/sample.json")

    # with open("../data/mappingrules_liub_custom_20211019.json", "r") as file:
    #     data = json.load(file)

    # res = folio.updateMappingRules(data)
    # print(res)

    # res = folio.restoreMappingRules()


if __name__ == '__main__':
    logging.basicConfig(
        format='%(levelname)s: %(message)s', level=logging.ERROR)

    logging.info('Startar en Folio-session.')
    folio = FolioCommunication()

    # folio.deleteServicePoint('01402059-bdcd-4f5e-a6ae-285cfe2730ac')
    # folio.deleteServicePoint('06239465-2997-447f-b9c8-5ecfb4f6ddf4')
    # folio.deleteServicePoint('9c8d405b-5ee7-4b56-bf92-a4a3063ae114')
    # folio.deleteServicePoint('c4c90014-c8c9-4ade-8f24-b5e313319f4b')

    # result = folio.getConfigurationsAudit()
    # print(result)

    # demo_libris_import(folio)
    # demo_update_mapping_rules(folio)

    # logging.info('Kollar om en användare finns.')
    # user = folio.userExists('DNF')
    # if user:
    #     user_uuid = folio.getUserUUID(user)

    # address_types = folio.getAddressTypes()

    # logging.info('Hämtar grupper.')
    # folio.getGroups()

    # logging.info('Skapar användare')
    # res = folio.createUser()
    # print(res)

    # if user:
    #     logging.info('Tar bort användare.')
    #     folio.deleteUser(user_uuid)

    # logging.info('Hämtar materialtyper.')
    # folio.getMaterialTypes()

    # logging.info('Hämtar intanser baserat på söksträng.')
    # folio.getInstances('interesting')

    # logging.info('Försöker ta bort en instans.')
    # folio.deleteInstance('a89eccf0-57a6-495e-898d-32b9b2210f2f')
