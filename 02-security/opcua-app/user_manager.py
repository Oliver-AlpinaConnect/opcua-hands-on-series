import dataclasses
import logging
from asyncua import ua
from asyncua.server.user_managers import UserManager
from asyncua.crypto.permission_rules import User, UserRole, SimpleRoleRuleset

class FanUserManager(UserManager):
    def __init__(self):
        self.users = {"manager": "admin456"}

    def get_user(self, iserver, username=None, password=None, certificate=None):
        # 1. Check for Username/Password (Authenticated)
        if username is not None:
            if username == "manager" and password == self.users.get(username):
                logging.info(f"User '{username}' authenticated as Admin.")
                return User(role=UserRole.Admin, name=username)
            logging.warning(f"Auth failed for: {username}")
            return None # Explicit rejection

        # 2. Handle Anonymous session request
        # Return a User object with Anonymous role; returning None here triggers your error
        logging.info("Granting Anonymous User Role.")
        return User(role=UserRole.Anonymous)

class Ruleset(SimpleRoleRuleset):
    ANON_TYPES = [
        ua.ObjectIds.CreateSessionRequest_Encoding_DefaultBinary,
        ua.ObjectIds.CloseSessionRequest_Encoding_DefaultBinary,
        ua.ObjectIds.ActivateSessionRequest_Encoding_DefaultBinary,
        ua.ObjectIds.ReadRequest_Encoding_DefaultBinary,
        ua.ObjectIds.BrowseRequest_Encoding_DefaultBinary,
        ua.ObjectIds.GetEndpointsRequest_Encoding_DefaultBinary,
        ua.ObjectIds.FindServersRequest_Encoding_DefaultBinary,
        ua.ObjectIds.TranslateBrowsePathsToNodeIdsRequest_Encoding_DefaultBinary,
        ua.ObjectIds.CloseSecureChannelRequest_Encoding_DefaultBinary,
        ua.ObjectIds.CallRequest_Encoding_DefaultBinary,
        ua.ObjectIds.RegisterNodesRequest_Encoding_DefaultBinary,
        ua.ObjectIds.UnregisterNodesRequest_Encoding_DefaultBinary,
    ]

    
    def __init__(self):
        super().__init__()
        anon_ids = list(map(ua.NodeId, self.ANON_TYPES))
        self._permission_dict[UserRole.Anonymous] = set().union(anon_ids)

    def check_validity(self, user, action_type_id, body):
        # 1. Run the base logic
        if not super().check_validity(user, action_type_id, body):
            return False

        # 2. Specifically block Writes for Anonymous 
        # (even if WriteRequest is in USER_TYPES)
        write_request_id = ua.NodeId(ua.ObjectIds.WriteRequest_Encoding_DefaultBinary)
        if action_type_id == write_request_id:
            if user.role == UserRole.Anonymous:
                # Check if they are trying to write to a protected node
                logging.warning(f"Anon Write Denied")
                return False
        return True


async def change_user_access_level(event, dispatcher):
# 1. Target only Anonymous users (leaving Admin/Manager with full access)
    if event.user.role == UserRole.Anonymous:
        
        # 2. Loop through the requested attributes
        for i, node_to_read in enumerate(event.request_params.NodesToRead):
            
            # 3. If the client is asking for UserAccessLevel
            if node_to_read.AttributeId == ua.AttributeIds.UserAccessLevel:
                
                # 4. FIX: Use dataclasses.replace to create a NEW DataValue object.
                # You cannot modify event.response_params[i].Value directly.
                new_value = ua.Variant(
                    ua.AccessLevel.CurrentRead.mask, 
                    ua.VariantType.Byte
                )
                
                # Replace the entire object in the list
                event.response_params[i] = dataclasses.replace(
                    event.response_params[i], 
                    Value=new_value
                )