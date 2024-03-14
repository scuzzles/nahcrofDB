require 'uri'
require 'net/http'
require 'json'
$api_key = []
$username = []

module NahcrofDB
    def self.init(api_key, location)
        $api_key << api_key
        $username << location
    end
    
    def self.getKey(keyname)
        uri = URI("https://database.nahcrof.com/getKey/?location=#{$username[0]}&keyname=#{keyname}&token=#{$api_key[0]}")
        res = Net::HTTP.get_response(uri)
        json_string = res.body if res.is_a?(Net::HTTPSuccess)
        parsed_json = JSON.parse(json_string)
        return parsed_json["keycontent"]
    end
    
    def self.makeKey(keyname, keycontent)
      url = URI("https://database.nahcrof.com/makeKey")
      http = Net::HTTP.new(url.host, url.port)

      http.use_ssl = (url.scheme == "https")

      request = Net::HTTP::Post.new(url)
      request["Content-Type"] = "application/json"
      request["Accept"] = "application/json"
      request.body = JSON.generate({ location: $username[0], keyname: keyname, keycontent: keycontent, token: $api_key[0] })

      response = http.request(request)

      case response
      when Net::HTTPSuccess
        parsed_json = response.body
        return parsed_json
      else
        puts "HTTP Error: #{response.code}"
        puts "Response body: #{response.body}"
        return nil
      end
    end

    def self.getAll()
        uri = URI("https://database.nahcrof.com/getAll/?location=#{$username[0]}&token=#{$api_key[0]}")
        res = Net::HTTP.get_response(uri)
        json_string = res.body if res.is_a?(Net::HTTPSuccess)
        parsed_json = JSON.parse(json_string)
        return "get all function has been deprecated" 
    end

    def self.delKey(keyname)
        url = URI("https://database.nahcrof.com/delKey")
        http = Net::HTTP.new(url.host, url.port)
        
        http.use_ssl = (url.scheme == "https")
        
        request = Net::HTTP::Post.new(url)
        request["Content-Type"] = "application/json"
        request["Accept"] = "application/json"
        request.body = JSON.generate({ location: $username[0], keyname: keyname, token: $api_key[0] })

        response = http.request(request)

        case response
        when Net::HTTPSuccess
            parsed_json = response.body
            return parsed_json
        else
            puts "HTTP Error: #{response.code}"
            puts "Response body: #{response.body}"
            return nil
        end
    end

    def self.resetDB()
        url = URI("https://database.nahcrof.com/resetDB")
        http = Net::HTTP.new(url.host, url.port)

        http.use_ssl = (url.scheme == "https")

        request = Net::HTTP::Post.new(url)
        request["Content-Type"] = "application/json"
        request["Accept"] = "application/json"
        request.body = JSON.generate({ location: $username[0], token: $api_key[0] })

        response = http.request(request)

        case response
        when Net::HTTPSuccess
            parsed_json = response.body
            return parsed_json
        else
            puts "HTTP Error: #{response.code}"
            puts "Response body: #{response.body}"
            return nil
        end
    end
end
