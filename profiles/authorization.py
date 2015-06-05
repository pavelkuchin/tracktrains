from tastypie.authorization import Authorization


class UserAuthorization(Authorization):
    def read_list(self, object_list, bundle):
        return object_list.filter(id=bundle.request.user.pk)

    def read_detail(self, object_list, bundle):
        return bundle.obj == bundle.request.user

    # TODO check tastypie sources, seems that to date tastypie
    # does not use this method
    def create_list(self, object_list, bundle):
        return object_list.filter(id=bundle.request.user.pk)

    def create_detail(self, object_list, bundle):
        return bundle.obj == bundle.request.user

    # TODO check tastypie sources, seems that for now tastypie
    # does not use this method
    def update_list(self, object_list, bundle):
        return object_list.filter(id=bundle.request.user.pk)

    def update_detail(self, object_list, bundle):
        return bundle.obj == bundle.request.user

    def delete_list(self, object_list, bundle):
        return object_list.filter(id=bundle.request.user.pk)

    def delete_detail(self, object_list, bundle):
        return bundle.obj == bundle.request.user
