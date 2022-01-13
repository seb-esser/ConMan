using System.Diagnostics;
using RestSharp;

namespace TransactionTracker
{
    public class ServerConnector
    {
        public string BaseUrl
        {
            get => "http://localhost:5000";
            set => throw new System.NotImplementedException();
        }

        public ServerConnector()
        {
        }

        public void PerformPostRequest(string target, object msg)
        {
            var uri = this.BaseUrl + target;
            var client = new RestClient(uri);
            var request = new RestRequest(uri, Method.POST);
            request.AddJsonBody(msg);

            Debug.WriteLine("[SERVER]: Sending Request ...");
            var res = client.Execute<string>(request);
            Debug.WriteLine($"[SERVER]: Response: {res.StatusCode}");

        }

    }
}