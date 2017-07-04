from allauth.socialaccount.adapter import DefaultSocialAccountAdapter


class CustomAdapter(DefaultSocialAccountAdapter):

    def populate_user(self, request, sociallogin, data):
        """
        Required to bypass the automatic user population
        """
        pass

    def get_signup_form_initial_data(self, sociallogin):
        """
        Required to bypass automatic initial form data override
        """
        pass