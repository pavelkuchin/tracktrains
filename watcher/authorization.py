from utils.authorization import OwnerBasedAuthorization


class TaskAuthorization(OwnerBasedAuthorization):
    def __limit_exceed(self, object_list, bundle):
        limit = bundle.request.user.tasks_limit
        count = object_list.count()
        return count >= limit


    def create_list(self, object_list, bundle):
        if self.__limit_exceed(object_list, bundle):
            return None
        else:
            return super(TaskAuthorization, self).create_list(object_list, bundle)

    def create_detail(self, object_list, bundle):
        if self.__limit_exceed(object_list, bundle):
            return False
        else:
            return super(TaskAuthorization, self).create_detail(object_list, bundle)
