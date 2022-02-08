import apiService from "./api";
import { message } from "antd";

class SearchResultService {
  
  async getSearchCards(payload) {
    const response = await apiService.post("cueSearch/getCards/", payload);
    if (response.success) {
      console.log("Response Data",response.data);
      return response;
      
    } else {
      message.error(response.message);
      return response;
    }
  }

  async getSearchCardsData(payload) {
    const response = await apiService.post("cueSearch/getSearchCardsData/", payload);
    if (response.success) {
      return response;
    } else {
      message.error(response.message);
      return response;
    }
  }

  async getSearchSuggestions(payload) {
    const response = await apiService.post(
      "cueSearch/searchsuggestions/",
      payload
    );
    return response;
  }
}

let searchResultService = new SearchResultService();
export default searchResultService;
