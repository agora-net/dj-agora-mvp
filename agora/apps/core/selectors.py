from agora.apps.core.models import WaitingList


def get_waiting_list_count():
    return WaitingList.objects.count()
