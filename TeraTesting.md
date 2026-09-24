# Tera Testing

This is the original prompt used to build the test suite with Sonnet.

## Problem

The Teradata Tera agent does not have an eval set that would allow regression testing 

## Solution

Build a agentic eval set for regression testing the Teradata Tera agent.


## Workflow

- plan that: 
	1. researches the typical prompts that would be asked to a helpful Teradata agent, these should include the following personas: business user, data scientist, data analyst, DBA, Security expert, database operations.
	2. creates the dependant database structures and data for the tests
	3. builds the eval test cases including:
		- typical use cases
		- edge use cases

- build:
	1. the Teradata database scripts 
	2. build the evals structures

- verify:
	1. that the database scripts are Teradata syntax
	2. that the evals are using the database data and structures

## Deliverables

### Format

Database
- script containing create database and create table scripts 
- script to populate the database tables with data


Evals
- use swagger for capturing test cases
- test cases should include an: id, name, category, description, prompt, expected output

### Definition of done
Datbase
- Scripts have been verify as Teradata syntax
- Data should be querable across tables (joins should work)

Evals
- each persona has a suite of use cases covering typical activities as well as edge activities

## How you are graded

- You'll be graded on a continuous basis based on every completed bullet in the definition of done
- Every step of workflow must be fully accomplished: plan, build, verify
- if you find you've mistakenly caused a failure stop immediately and report your failure
