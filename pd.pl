#!/usr/bin/perl

use strict;
use warnings;
use Data::Dumper;

our %tdata ;

{
  foreach my $f (@ARGV) {
    if ($f =~ /^javacore/) {
      process_javacore($f) ;
    }
    elsif ($f =~ /^top/) {
      process_top($f) ;
    }
    else { die "unrecognized file $f" ; }
  }
  foreach my $k (sort (keys %tdata)) {
    print "$k\n" ;
    print int(@{ $tdata{$k} })." lines\n";
  }
}

sub process_javacore {
  my $f = shift;

  my $jctime ;
  my $threadName ;
  open(F,"<$f") || die "cannot open $f fo reading" ;
  while (<F>) {
    chomp ;
    if ($_ =~ /^1TIDATETIME\s+Date:\s+(\S+) at (\S+)/) {
      $jctime = $2 ;
    }
    elsif ($_ =~ /^3XMTHREADINFO\s+"([^"]+)"/) {
      $threadName = $1 ;
    }
    elsif ($_ =~ /^3XMTHREADINFO      Anonymous native thread/) {
      $threadName = "<anonymous>" ;
    }
    elsif ($_ =~ /^3XMTHREADINFO1\s+\(native thread ID:([^,]+)/) {
      my $threadId = $1 ;
      die "internal error -- is your javacore mangled?"
	unless (defined $jctime && defined $threadName) ;
      my $jcdata = [$jctime, $threadId, $threadName] ;
      undef $threadName ;
      print Dumper($jcdata),"\n";
    }
  }
  close(F) ;
}

sub process_top {
  my $f = shift;
  open(F,"<$f") || die "cannot open $f for reading" ;
  my @lines = () ;
  while(<F>) {
    chomp ;
    if ($_ =~ /^top/) {
      if (int(@lines)) {
	$tdata{$lines[0]} = [@lines] ;
	@lines = () ;
      }
    }
    push(@lines, $_) ;
  }

  if (int(@lines)) {
    $tdata{$lines[0]} = [@lines] ;
    @lines = () ;
  }
  close(F) ;
}
