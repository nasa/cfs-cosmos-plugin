# encoding: ascii-8bit

# Create the overall gemspec
Gem::Specification.new do |s|
  s.name = 'openc3-cosmos-cfs'
  s.summary = 'OpenC3 openc3-cosmos-cfs plugin'
  s.description = <<-EOF
    openc3-cosmos-cfs plugin for deployment to OpenC3
  EOF
  s.license = 'Apache-2.0'
  s.authors = ['NASA']
  s.email = ['cfs-program@lists.nasa.gov']
  s.homepage = 'https://github.com/nasa/cfs'
  s.platform = Gem::Platform::RUBY

  s.metadata = {
    "source_code_uri" => "https://github.com/nasa/cfs-cosmos-plugin",
    "openc3_store_title" => "NASA cFS Integration",
    "openc3_store_description" => "This NASA OpenC3 COSMOS plugin is used to control and test the core Flight System (cFS) Flight Software (FSW).",
    "openc3_store_image" => "public/store_img.png",
    "openc3_store_keywords" => "nasa, core, flight software, cfs, fsw",
    "openc3_cosmos_minimum_version" => "5.13.0"
  }

  if ENV['VERSION']
    s.version = ENV['VERSION'].dup
  else
    time = Time.now.strftime("%Y%m%d%H%M%S")
    s.version = '7.0.0' + ".#{time}"
  end
  s.files = Dir.glob("{targets,lib,public,tools,microservices}/**/*") + %w(Rakefile README.md LICENSE.txt plugin.txt requirements.txt)
end
