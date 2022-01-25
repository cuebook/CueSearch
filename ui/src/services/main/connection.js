import apiService from "./api";

class ConnectionService {
  async getConnections() {
    const response = await apiService.get("dataset/connections");
    return response;
  }

  async getConnection(connectionId) {
    const response = await apiService.get("dataset/connection/" + connectionId);
    return response;
  }

  async getConnectionTypes() {
    const response = await apiService.get("dataset/connectiontypes");
    return response;
  }

  async addConnection(payload) {
    const response = await apiService.post("dataset/connections", payload);
    return response;
  }

  async updateConnection(connectionId, payload) {
    const response = await apiService.put(
      "dataset/connection/" + connectionId,
      payload
    );
    return response;
  }

  async deleteConnection(connectionId) {
    const response = await apiService.delete(
      "dataset/connection/" + connectionId
    );
    return response;
  }
}
let connectionService = new ConnectionService();
export default connectionService;
