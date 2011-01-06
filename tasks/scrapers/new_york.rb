require 'rubygems'
require 'open-uri'
require 'nokogiri'

def print_to_file(item, file)
  file << [
    item[:title],
    item[:venue],
    item[:address1],
    item[:address2],
    item[:date],
    item[:description],
    item[:url],
    item[:cost]
  ].join("\t") + "\n"
end

def print_item(item)
  puts "Title:    #{item[:title]}"
  puts "=================================================="
  puts "Date:     #{item[:date]}"
  puts "Showtime: #{item[:showtime]}"
  puts "Location: #{item[:location]}"
  puts "Venue:    #{item[:venue]}"
  puts "Address1: #{item[:address1]}"
  puts "Address2: #{item[:address2]}"
  puts "Cost:     #{item[:cost]}"
  puts "Desc:     #{item[:description]}"
  puts "URL:      #{item[:url]}"
  puts
end

def clean(item)  
  # COST
  if item[:cost].class == String
    cost = /(\d+(\.[0-9]+)?)/
    m = cost.match(item[:cost])
    if m
      item[:cost] = m[0].to_f
    else
      item[:cost] = 0
    end
  end

  # Fix DATE
  if item[:date][" at "]:
    parts = item[:date].split(" at ")
    item[:date] = parts[0]
    if item[:location].empty? and parts[1] != nil?
      item[:location] = parts[1]
    end
  end

  # Collapse LOCATION and VENUE into VENUE
  if (item[:location] == nil or item[:location].empty?) and item[:title]["@"] != nil:
    parts = item[:title].split("@")
    item[:title] = parts[0].strip!
    item[:location] = parts[1].strip!
  end
  
  if (not item.has_key?(:venue)) or item[:venue] == nil or item[:venue].empty? or item[:venue] == '':
    item[:venue] = item[:location]
  end 
  
  item.delete(:location)
  
  # Clean all tabs and newlines out
  cleaned = {}
  item.each do |k,v|
    if v.class == String
      v.gsub!(/\s/,' ')
      v = '' if v == nil
      v.strip!
    end
    cleaned[k] = v
  end
  
  return cleaned
end

def parse_ny(url)
  items = []
  until url == nil
    doc = Nokogiri::HTML(open(url))
    doc.xpath('//div[@class="item"]').each do |i|
      item = {}
      item[:title] = i.xpath('.//h5[@class="title"]').first.text rescue ""
      item[:url] = 'http://www.nyc.com' + i.xpath('.//h5[@class="title"]/a').first.attributes["href"].value rescue ""
      item[:description] = i.xpath('.//p').first.text rescue ""
      item[:date] = i.xpath('.//h5[@class="title"]').first.next_sibling().text rescue ""
      item[:location] = i.xpath('.//h5[@class="title"]').first.next_sibling().next_sibling().text rescue ""
      item[:showtime] = i.xpath('.//div[@class="timePlace"]').xpath('.//h3').first.text rescue ""
      item[:venue] = i.xpath('.//div[@class="timePlace"]').xpath('.//h3').first.next_sibling().text rescue ""
      item[:address1] = i.xpath('.//div[@class="timePlace"]').xpath('.//h3').first.next_sibling().next_sibling().next_sibling().text rescue ""
      item[:address2] = i.xpath('.//div[@class="timePlace"]').xpath('.//h3').first.next_sibling().next_sibling().next_sibling().next_sibling().next_sibling().text   rescue ""
    
      c = i.xpath('.//div[@class="cost"]')  
      if c.size > 0
        item[:cost] = i.xpath('.//div[@class="cost"]').first.text
      else
        item[:cost] = 0
      end
      items << item
    end
    url = nil
    kids = doc.xpath('//div[@class="botNav"]').children
    kids.each do |k|
      if k != nil and k.text == "Next 20" and k.name == "a"
        url = 'http://www.nyc.com/events/' + k.attributes["href"].value
      end
    end
    doc.xpath('//div[@class="botNav"]')
  end
  return items.map {|i| clean(i)}
end

if ARGV.length < 3
  filename = 'foo.csv'
  start = '09/08/2010'
  stop = '09/14/2010'
else
  filename = ARGV[0]
  start = ARGV[1]
  stop = ARGV[2]
end

events = parse_ny("http://www.nyc.com/events/?secid=30&from=#{start}&to=#{stop}&sort=e&int4=5&category=49#list")

File.open(filename, 'w') do |f|
  events.each do |e|
    print_to_file(e,f)
  end
end
