from datetime import datetime

from flask_jwt_extended import decode_token
from sqlalchemy.orm.exc import NoResultFound

from call_records.model.tokenblacklist import TokenBlacklist
from call_records import db

class TokenBlackListService(object):

    def _epoch_utc_to_datetime(self, epoch_utc):
        """
        Helper function for converting epoch timestamps (as stored in JWTs) into
        python datetime objects (which are easier to use with sqlalchemy).
        """
        return datetime.fromtimestamp(epoch_utc)

    def revoke_user_token(self, user):
        """ Revoke any unrevoked token for this user """
        olds_token = TokenBlacklist.query.filter(
            TokenBlacklist.user_identity==user and TokenBlacklist.revoked==False
        ).all()
        for token in olds_token:
            token.revoke()

    def add_token_to_database(self, encoded_token, identity_claim):
        """
        Adds a new token to the database. It is not revoked when it is added.
        :param identity_claim:
        """
        decoded_token = decode_token(encoded_token)

        jti = decoded_token['jti']
        token_type = decoded_token['type']
        user_identity = decoded_token[identity_claim]
        expires = self._epoch_utc_to_datetime(decoded_token['exp'])
        revoked = False

        #Revoke any unrevoked access token for this user
        self.revoke_user_token(user_identity)

        db_token = TokenBlacklist(
            jti=jti,
            token_type=token_type,
            user_identity=user_identity,
            expires=expires,
            revoked=revoked,
        )
        db_token.save()


    def is_token_revoked(self, decoded_token):
        """
        Checks if the given token is revoked or not. If an token isn't found in this
        database we consider as revoked (just in case of refresh tokens),
        because we dont save all tokens, just the refresh tokens.
        """
        jti = decoded_token['jti']
        token_type = decoded_token['type']

        if token_type == 'access':
            return False

        try:
            token = TokenBlacklist.query.filter_by(jti=jti).one()
            return token.revoked
        except NoResultFound:
            return True


    def get_user_tokens(self, user_identity):
        """
        Returns all of the tokens, revoked and unrevoked, that are stored for the
        given user
        """
        return TokenBlacklist.query.filter_by(user_identity=user_identity).all()


    def revoke_token(self, jti, user):
        """
        Revokes the given token. Raises a TokenNotFound error if the token does
        not exist in the database
        """
        try:
            token = TokenBlacklist.query.filter_by(jti=jti, user_identity=user).one()
            token.revoke()
        except NoResultFound:
            pass

    def unrevoke_token(self, token_id, user):
        """
        Unrevokes the given token. Raises a TokenNotFound error if the token does
        not exist in the database
        """
        try:
            token = TokenBlacklist.query.filter_by(id=token_id, user_identity=user).one()
            token.revoked = False
            token.save()
        except NoResultFound:
            pass


    def prune_database(self):
        """
        Delete tokens that have expired from the database.
        How (and if) you call this is entirely up you. You could expose it to an
        endpoint that only administrators could call, you could run it as a cron,
        set it up with flask cli, etc.
        """
        now = datetime.now()
        expired = TokenBlacklist.query.filter(TokenBlacklist.expires < now).all()
        for token in expired:
            token.delete()
