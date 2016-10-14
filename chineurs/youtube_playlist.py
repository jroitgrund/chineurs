'''Functions to interact with YouTube playlists'''
import apiclient
import httplib2


def list_playlist_contents(credentials, playlist_id):
    '''Gets a list of current playlist video titles'''
    http = httplib2.Http()
    http = credentials.authorize(http)

    service = apiclient.discovery.build('youtube', 'v3', http=http)
    request = service.playlistItems().list(  # pylint:disable=no-member
        part='snippet', playlistId=playlist_id)
    titles = []
    while request is not None:
        response = request.execute()
        titles.extend(
            video['snippet']['title'] for video in response.get('items', []))
        # pylint:disable=no-member
        request = service.playlistItems().list_next(request, response)
    return titles
