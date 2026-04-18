CREATE MIGRATION m1ib24z6xtirxntmdgwtexy7wyr6hxs3plnjqe7cxioypwc5c7dtja
    ONTO m1moxkyxncruylrsf2tcxyv4mcsontjpmmup6grbiwv7jro65w3tuq
{
  CREATE TYPE default::JobOpportunity {
      CREATE REQUIRED PROPERTY company: std::str;
      CREATE REQUIRED PROPERTY embedding: array<std::float32>;
      CREATE REQUIRED PROPERTY is_remote: std::bool;
      CREATE REQUIRED PROPERTY job_type: std::str;
      CREATE REQUIRED PROPERTY link: std::str {
          CREATE CONSTRAINT std::exclusive;
      };
      CREATE REQUIRED PROPERTY location: std::str;
      CREATE PROPERTY published: std::str;
      CREATE PROPERTY salary_range: std::str;
      CREATE REQUIRED PROPERTY seniority: std::str;
      CREATE REQUIRED PROPERTY skills: array<std::str>;
      CREATE REQUIRED PROPERTY title: std::str;
  };
  DROP EXTENSION pgvector;
};
